# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2019 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Models for REANA Components."""

from __future__ import absolute_import

import enum
import math
import uuid
from datetime import datetime

from reana_commons.utils import get_disk_usage
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    event,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EncryptedType, JSONType, UUIDType
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from reana_db.config import DB_SECRET_KEY, DEFAULT_QUOTA_LIMITS, DEFAULT_QUOTA_RESOURCES
from reana_db.utils import (
    build_workspace_path,
    store_workflow_disk_quota,
    get_default_quota_resource,
    update_users_disk_quota,
)

Base = declarative_base()


def generate_uuid():
    """Generate new uuid."""
    return str(uuid.uuid4())


class User(Base, Timestamp):
    """User table."""

    __tablename__ = "user_"
    __table_args__ = {"schema": "__reana"}

    id_ = Column(UUIDType, primary_key=True, unique=True, default=generate_uuid)
    email = Column(String(length=255), unique=True, primary_key=True)
    full_name = Column(String(length=255))
    username = Column(String(length=255))
    tokens = relationship("UserToken", backref="user_", lazy="dynamic")
    workflows = relationship("Workflow", backref="user_", lazy="dynamic")
    audit_logs = relationship("AuditLog", backref="user_")
    resources = relationship("UserResource", backref="user_")

    def __init__(self, access_token=None, **kwargs):
        """Initialize user model."""
        for k, v in kwargs.items():
            setattr(self, k, v)
        if access_token:
            self.access_token = access_token
        self.initialize_user_quota_limits()

    @hybrid_property
    def active_token(self):
        """REANA active access token object."""
        return self.tokens.filter_by(
            status=UserTokenStatus.active, type_=UserTokenType.reana
        ).one_or_none()

    @hybrid_property
    def access_token(self):
        """REANA active access token value."""
        return self.active_token.token if self.active_token else None

    @access_token.setter
    def access_token(self, value):
        """REANA access token setter."""
        from .database import Session

        if self.tokens.count() and self.active_token:
            raise Exception("User {} has already an active access token.".format(self))
        if (
            self.tokens.count()
            and self.access_token_status == UserTokenStatus.requested.name
        ):
            self.latest_access_token.status = UserTokenStatus.active
            self.latest_access_token.token = value
        else:
            user_token = UserToken(
                user_=self,
                token=value,
                status=UserTokenStatus.active,
                type_=UserTokenType.reana,
            )
            Session.add(user_token)

    @hybrid_property
    def latest_access_token(self):
        """REANA most recent access token."""
        latest_reana_token = (
            self.tokens.filter_by(type_=UserTokenType.reana).order_by(
                UserToken.created.desc()
            )
        ).first()
        return latest_reana_token or None

    @hybrid_property
    def access_token_status(self):
        """REANA most recent access token status."""
        return (
            self.latest_access_token.status.name if self.latest_access_token else None
        )

    def get_user_workspace(self):
        """Build user's workspace directory path.

        :return: Path to the user's workspace directory.
        """
        return build_workspace_path(self.id_)

    def get_user_quota_by_type(self, resource_type):
        """Aggregate user quota usage by resource type."""

        def _get_health_status(usage, limit):
            """Calculate quota health status."""
            health = QuotaHealth.healthy
            if limit:
                percentage = usage / limit * 100
                if percentage >= 60:
                    if percentage >= 85:
                        health = QuotaHealth.critical
                    else:
                        health = QuotaHealth.warning
            return health.name

        quota_usage = 0
        quota_limit = 0
        unit = None
        for user_resource in self.resources:
            if user_resource.resource.type_ == resource_type:
                # make sure that all resources of the same type use the same units
                if unit and unit != user_resource.resource.unit:
                    raise Exception(
                        "Error while calculating quota usage. Not all "
                        "resources of resource type {} use "
                        "the same units.".format(resource_type)
                    )
                unit = user_resource.resource.unit
                quota_usage += user_resource.quota_used
                quota_limit += user_resource.quota_limit

        quota_human_readable_usage = ResourceUnit.human_readable_unit(unit, quota_usage)
        quota_human_readable_limit = ResourceUnit.human_readable_unit(unit, quota_limit)

        return {
            "usage": {
                "raw": quota_usage,
                "human_readable": quota_human_readable_usage,
            },
            "limit": {
                "raw": quota_limit,
                "human_readable": quota_human_readable_limit,
            },
            "health": _get_health_status(quota_usage, quota_limit),
        }

    def request_access_token(self):
        """Create user token and mark it as requested."""
        from .database import Session

        if self.tokens.count() and self.active_token:
            raise Exception("User {} has already an active access token.".format(self))
        if (
            self.tokens.count()
            and self.access_token_status == UserTokenStatus.requested.name
        ):
            raise Exception(
                "User {} has already requested an access" " token.".format(self)
            )
        user_token = UserToken(
            user_=self,
            token=None,
            status=UserTokenStatus.requested,
            type_=UserTokenType.reana,
        )
        Session.add(user_token)
        Session.commit()

    def log_action(self, action, details=None):
        """Create audit log entry for the user.

        :param action: Type of action.
        :type action: AuditLogAction
        :param details: JSON field containing action details.
        """
        from .database import Session

        audit_log = AuditLog(user_id=self.id_, action=action, details=details)
        Session.add(audit_log)
        Session.commit()
        return audit_log

    def initialize_user_quota_limits(self):
        """Initialize user quota limits."""
        resources = Resource.query.all()
        for resource in resources:
            self.resources.append(
                UserResource(
                    user_id=self.id_,
                    resource_id=resource.id_,
                    quota_limit=DEFAULT_QUOTA_LIMITS[resource.type_.name],
                    quota_used=0,
                )
            )

    def get_quota_usage(self):
        """Get user quota usage information."""
        return dict(
            disk=self.get_user_quota_by_type(ResourceType.disk),
            cpu=self.get_user_quota_by_type(ResourceType.cpu),
        )

    def __repr__(self):
        """User string representation."""
        return "<User %r>" % self.id_


class UserTokenStatus(enum.Enum):
    """Enumeration of possible user token statuses."""

    requested = 0
    active = 1
    revoked = 2


class UserTokenType(enum.Enum):
    """Enumeration of possible user token types."""

    reana = 0


class UserToken(Base, Timestamp):
    """User tokens table."""

    __tablename__ = "user_token"
    __table_args__ = {"schema": "__reana"}

    id_ = Column(UUIDType, primary_key=True, default=generate_uuid)
    token = Column(
        EncryptedType(String(length=255), DB_SECRET_KEY, AesEngine, "pkcs5"),
        unique=True,
    )
    status = Column(Enum(UserTokenStatus))
    user_id = Column(UUIDType, ForeignKey("__reana.user_.id_"), nullable=False)
    type_ = Column(Enum(UserTokenType), nullable=False)


class RunStatus(enum.Enum):
    """Enumeration of possible run statuses."""

    created = 0
    running = 1
    finished = 2
    failed = 3
    deleted = 4
    stopped = 5
    queued = 6


ALLOWED_WORKFLOW_STATUS_TRANSITIONS = [
    # Creation
    (RunStatus.created, RunStatus.deleted),
    (RunStatus.created, RunStatus.running),
    # Running
    (RunStatus.running, RunStatus.failed),
    (RunStatus.running, RunStatus.finished),
    (RunStatus.running, RunStatus.stopped),
    (RunStatus.running, RunStatus.running),
    # Stopped
    (RunStatus.stopped, RunStatus.deleted),
    # Failed
    (RunStatus.failed, RunStatus.deleted),
    (RunStatus.failed, RunStatus.running),
    # Finished
    (RunStatus.finished, RunStatus.deleted),
    (RunStatus.finished, RunStatus.running),
]


class JobStatus(enum.Enum):
    """Enumeration of possible job statuses."""

    created = 0
    running = 1
    finished = 2
    failed = 3
    stopped = 4
    queued = 5


class WorkflowSession(Base):
    """Workflow Session table."""

    __tablename__ = "workflow_session"
    __table_args__ = {"schema": "__reana"}

    workflow_id = Column(UUIDType, ForeignKey("__reana.workflow.id_"), nullable=True)
    session_id = Column(
        UUIDType, ForeignKey("__reana.interactive_session.id_"), primary_key=True
    )

    def __repr__(self):
        """Workflow Session string representation."""
        return "<WorkflowSession {} {}>".format(self.session_id, self.workflow_id)


class InteractiveSessionType(enum.Enum):
    """Enumeration of interactive session types."""

    jupyter = 0


class InteractiveSession(Base, Timestamp):
    """Interactive Session table."""

    __tablename__ = "interactive_session"
    id_ = Column(UUIDType, primary_key=True, unique=True, default=generate_uuid)
    name = Column(String(255))
    path = Column(Text)  # path to access the interactive session
    status = Column(Enum(RunStatus), nullable=False, default=RunStatus.created)
    owner_id = Column(UUIDType, ForeignKey("__reana.user_.id_"))
    type_ = Column(
        Enum(InteractiveSessionType),
        nullable=False,
        default=InteractiveSessionType.jupyter,
    )

    __table_args__ = (
        UniqueConstraint("name", "path", name="_interactive_session_uc"),
        {"schema": "__reana"},
    )

    def __repr__(self):
        """Interactive Session string representation."""
        return "<InteractiveSession %r>" % self.name


class Workflow(Base, Timestamp):
    """Workflow table."""

    __tablename__ = "workflow"

    id_ = Column(UUIDType, primary_key=True)
    name = Column(String(255))
    status = Column(Enum(RunStatus), default=RunStatus.created)
    owner_id = Column(UUIDType, ForeignKey("__reana.user_.id_"))
    reana_specification = Column(JSONType)
    input_parameters = Column(JSONType)
    operational_options = Column(JSONType)
    type_ = Column(String(30))
    logs = Column(String)
    run_started_at = Column(DateTime)
    run_finished_at = Column(DateTime)
    run_stopped_at = Column(DateTime)
    _run_number = Column("run_number", Float)
    job_progress = Column(JSONType, default=dict)
    workspace_path = Column(String)
    restart = Column(Boolean, default=False)
    # job_progress = {
    #  jobs_total = {total: job_number}
    #  jobs_running = {job_ids: [], total: c}
    #  jobs_finished = {job_ids: [], total: c}
    #  jobs_failed = {job_ids: [], total: c}}
    engine_specific = Column(JSONType)
    git_ref = Column(String(40))
    git_repo = Column(String(255))
    git_provider = Column(String(255))
    owner = relationship("User", backref="workflow")

    sessions = relationship(
        "InteractiveSession",
        secondary="__reana.workflow_session",
        lazy="dynamic",
        backref="workflow",
        cascade="all, delete",
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "owner_id", "run_number", name="_user_workflow_run_uc"
        ),
        {"schema": "__reana"},
    )

    def __init__(
        self,
        id_,
        name,
        owner_id,
        reana_specification,
        type_,
        logs="",
        input_parameters={},
        operational_options={},
        status=RunStatus.created,
        git_ref="",
        git_repo=None,
        git_provider=None,
        workspace_path=None,
        restart=False,
        run_number=None,
    ):
        """Initialize workflow model."""
        self.id_ = id_
        self.name = name
        self.status = status
        self.owner_id = owner_id
        self.reana_specification = reana_specification
        self.input_parameters = input_parameters
        self.operational_options = operational_options
        self.type_ = type_
        self.logs = logs or ""
        self.git_ref = git_ref
        self.git_repo = git_repo
        self.git_provider = git_provider
        self.restart = restart
        self._run_number = self.assign_run_number(run_number)
        self.workspace_path = workspace_path or build_workspace_path(
            self.owner_id, self.id_
        )

    def __repr__(self):
        """Workflow string representation."""
        return "<Workflow %r>" % self.id_

    @hybrid_property
    def run_number(self):
        """Property of run_number."""
        if self._run_number.is_integer():
            return int(self._run_number)
        return self._run_number

    @run_number.expression
    def run_number(cls):
        return func.abs(cls._run_number)

    def assign_run_number(self, run_number):
        """Assing run number."""
        from .database import Session

        if run_number:
            last_workflow = (
                Session.query(Workflow)
                .filter(
                    Workflow.name == self.name,
                    Workflow.run_number >= int(run_number),
                    Workflow.run_number < int(run_number) + 1,
                    Workflow.owner_id == self.owner_id,
                )
                .order_by(Workflow.run_number.desc())
                .first()
            )
        else:
            last_workflow = (
                Session.query(Workflow)
                .filter_by(name=self.name, restart=False, owner_id=self.owner_id)
                .order_by(Workflow.run_number.desc())
                .first()
            )
        if last_workflow and self.restart:
            return round(last_workflow.run_number + 0.1, 1)
        else:
            if not last_workflow:
                return 1
            else:
                return last_workflow.run_number + 1

    def get_input_parameters(self):
        """Return workflow parameters."""
        return self.reana_specification.get("inputs", {}).get("parameters", {})

    def get_specification(self):
        """Return workflow specification."""
        return self.reana_specification["workflow"].get("specification", {})

    def get_owner_access_token(self):
        """Return workflow owner access token."""
        from .database import Session

        db_session = Session.object_session(self)
        owner = db_session.query(User).filter_by(id_=self.owner_id).first()
        return owner.access_token

    def get_full_workflow_name(self):
        """Return full workflow name including run number."""
        return "{}.{}".format(self.name, str(self.run_number))

    def get_workspace_disk_usage(self, summarize=False, block_size=None):
        """Retrieve disk usage information of a workspace."""
        from .database import Session

        def _format_disk_usage(bytes_, block_size):
            """Format disk usage according to passed args."""
            if block_size:
                # TODO: Change when https://github.com/reanahub/reana-server/issues/296
                # gets implemented.
                size = (
                    "{}B".format(bytes_)
                    if block_size == "b"
                    else "{}K".format(round(bytes_ / 1024, 2))
                )
            else:
                size = str(bytes_)
            return [{"name": "", "size": size}]

        if not summarize:
            # size break down per directory so we can't query DB (`r-client du`)
            return get_disk_usage(self.workspace_path, summarize, block_size)

        disk_resource = get_default_quota_resource(ResourceType.disk.name)
        disk_bytes = (
            Session.query(WorkflowResource.quantity_used)
            .filter_by(workflow_id=self.id_, resource_id=disk_resource.id_)
            .scalar()
        )
        if disk_bytes:
            return _format_disk_usage(disk_bytes, block_size)

        # recalculate disk workflow resource
        workflow_resource = store_workflow_disk_quota(self)
        return _format_disk_usage(workflow_resource.quantity_used, block_size)

    @staticmethod
    def update_workflow_status(
        db_session, workflow_uuid, status, new_logs="", message=None
    ):
        """Update database workflow status.

        :param workflow_uuid: UUID which represents the workflow.
        :param status: String that represents the workflow status.
        :param new_logs: New logs from workflow execution.
        :param message: Unused.
        """
        try:
            workflow = db_session.query(Workflow).filter_by(id_=workflow_uuid).first()

            if not workflow:
                raise Exception(
                    "Workflow {0} doesn't exist in database.".format(workflow_uuid)
                )
            if status:
                workflow.status = status
            if new_logs:
                workflow.logs = (workflow.logs or "") + new_logs + "\n"
            db_session.commit()
        except Exception as e:
            raise e

    def can_transition_to(self, next_status):
        """Whether the provided workflow can transition to the next status."""
        current_transition = (self.status, next_status)
        return current_transition in ALLOWED_WORKFLOW_STATUS_TRANSITIONS

    def update_workflow_timestamp(self, new_status):
        """Update workflow timestamps according to new status."""
        from .database import Session

        if new_status in [
            RunStatus.finished,
            RunStatus.failed,
        ]:
            self.run_finished_at = datetime.now()
        elif new_status in [RunStatus.stopped]:
            self.run_stopped_at = datetime.now()
        elif new_status in [RunStatus.running]:
            self.run_started_at = datetime.now()
        Session.commit()


@event.listens_for(Workflow.status, "set")
def workflow_status_change_listener(workflow, new_status, old_status, initiator):
    """Workflow status change listener."""
    from .database import Session

    def _update_disk_quota(workflow):
        update_users_disk_quota(user=workflow.owner)
        store_workflow_disk_quota(workflow)

    def _update_cpu_quota(workflow):
        terminated_at = workflow.run_finished_at or workflow.run_stopped_at
        if workflow.run_started_at and terminated_at:
            cpu_time = terminated_at - workflow.run_started_at
            cpu_milliseconds = int(cpu_time.total_seconds() * 1000)
            cpu_resource = get_default_quota_resource(ResourceType.cpu.name)
            workflow_resource = WorkflowResource(
                workflow_id=workflow.id_,
                resource_id=cpu_resource.id_,
                quantity_used=cpu_milliseconds,
            )
            user_resource_quota = UserResource.query.filter_by(
                user_id=workflow.owner_id, resource_id=cpu_resource.id_
            ).first()
            user_resource_quota.quota_used += cpu_milliseconds
            Session.add(workflow_resource)
            Session.commit()

    workflow.update_workflow_timestamp(new_status)
    if new_status in [
        RunStatus.finished,
        RunStatus.failed,
        RunStatus.stopped,
    ]:
        _update_cpu_quota(workflow)
        _update_disk_quota(workflow)
    elif new_status in [RunStatus.deleted]:
        _update_disk_quota(workflow)

    return new_status


class Job(Base, Timestamp):
    """Job table."""

    __tablename__ = "job"
    __table_args__ = {"schema": "__reana"}

    id_ = Column(UUIDType, primary_key=True, default=generate_uuid)
    backend_job_id = Column(String(256))
    workflow_uuid = Column(UUIDType)
    status = Column(Enum(JobStatus), default=JobStatus.created)
    compute_backend = Column(String(30))
    cvmfs_mounts = Column(Text)
    shared_file_system = Column(Boolean)
    docker_img = Column(String(256))
    cmd = Column(JSONType)
    env_vars = Column(JSONType)
    deleted = Column(Boolean)
    logs = Column(String, nullable=True)
    prettified_cmd = Column(JSONType)
    job_name = Column(Text)


class JobCache(Base, Timestamp):
    """Job Cache table."""

    __tablename__ = "job_cache"
    __table_args__ = {"schema": "__reana"}

    id_ = Column(UUIDType, primary_key=True, default=generate_uuid)
    job_id = Column(UUIDType, ForeignKey("__reana.job.id_"), primary_key=True)
    parameters = Column(String(1024))
    result_path = Column(String(1024))
    workspace_hash = Column(String(1024))
    access_times = Column(JSONType)


class AuditLogAction(enum.Enum):
    """Enumeration of audit log actions."""

    request_token = 0
    grant_token = 1
    revoke_token = 2


class AuditLog(Base, Timestamp):
    """Audit log table."""

    __tablename__ = "audit_log"
    __table_args__ = {"schema": "__reana"}

    id_ = Column(UUIDType, primary_key=True, default=generate_uuid)
    user_id = Column(UUIDType, ForeignKey("__reana.user_.id_"), nullable=False)
    action = Column(Enum(AuditLogAction), nullable=False)
    details = Column(JSONType)

    def __repr__(self):
        """Audit log string representation."""
        return "<AuditLog {} {}>".format(self.id_, self.action)


class ResourceType(enum.Enum):
    """Enumeration of resource types."""

    cpu = 0
    disk = 1


class ResourceUnit(enum.Enum):
    """Enumeration of resource usage units."""

    bytes_ = 0
    milliseconds = 1

    @staticmethod
    def _human_readable_milliseconds(milliseconds):
        """Convert milliseconds usage to human readable string."""
        hours, minutes, seconds = (
            milliseconds // (1000 * 60 * 60),
            (milliseconds // (1000 * 60)) % 60,
            (milliseconds // 1000) % 60,
        )

        human_readable_milliseconds = ""
        for value, unit in [(hours, "h"), (minutes, "m"), (seconds, "s")]:
            if value >= 1:
                human_readable_milliseconds += "{value}{unit} ".format(
                    value=value, unit=unit
                )

        return human_readable_milliseconds.strip() or "0s"

    @staticmethod
    def _human_readable_bytes(bytes_):
        """Convert bytes usage to human readable string."""
        if bytes_ == 0:
            return "0 Bytes"
        units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        digits = 2
        k = 1024
        unit_index = math.floor(math.log(bytes_) / math.log(k))

        converted_value = round(bytes_ / math.pow(k, unit_index), digits)
        return "{converted_value} {converted_unit}".format(
            converted_value=int(converted_value)
            if converted_value.is_integer()
            else converted_value,
            converted_unit=units[unit_index],
        )

    @staticmethod
    def human_readable_unit(unit, value):
        """Convert passed value in units to human readable string."""
        convert_to_human_readable = {
            ResourceUnit.bytes_: ResourceUnit._human_readable_bytes,
            ResourceUnit.milliseconds: ResourceUnit._human_readable_milliseconds,
        }
        return convert_to_human_readable[unit](value)


class Resource(Base, Timestamp):
    """Resource table."""

    __tablename__ = "resource"
    __table_args__ = {"schema": "__reana"}

    id_ = Column(UUIDType, primary_key=True, default=generate_uuid)
    name = Column(String(1024), unique=True, nullable=False)
    type_ = Column(Enum(ResourceType), nullable=False)
    unit = Column(Enum(ResourceUnit), nullable=False)
    title = Column(String(1024))

    def __repr__(self):
        """Resource string representation."""
        return "<Resource {}>".format(self.id_)

    @staticmethod
    def initialise_default_resources():
        """Initialise default Resources."""
        from reana_db.database import Session

        existing_resources = [r.name for r in Resource.query.all()]
        default_resources = []
        resource_type_to_unit = {
            ResourceType.cpu: ResourceUnit.milliseconds,
            ResourceType.disk: ResourceUnit.bytes_,
        }
        for type_, name in DEFAULT_QUOTA_RESOURCES.items():
            if name not in existing_resources:
                default_resources.append(
                    Resource(
                        name=name,
                        type_=ResourceType[type_],
                        unit=resource_type_to_unit[ResourceType[type_]],
                        title="Default {} resource.".format(type_),
                    )
                )

        if default_resources:
            Session.add_all(default_resources)
            Session.commit()

        return default_resources


class UserResource(Base, Timestamp):
    """User Resource table."""

    __tablename__ = "user_resource"
    __table_args__ = {"schema": "__reana"}

    user_id = Column(UUIDType, ForeignKey("__reana.user_.id_"), primary_key=True)
    resource_id = Column(UUIDType, ForeignKey("__reana.resource.id_"), primary_key=True)
    quota_limit = Column(BigInteger())
    quota_used = Column(BigInteger())
    user = relationship("User", backref="user_resource")
    resource = relationship("Resource", backref="user_resource")

    def __repr__(self):
        """User Resource string representation."""
        return "<UserResource {} {}>".format(self.user_id, self.resource_id)


class WorkflowResource(Base, Timestamp):
    """Workflow Resource table."""

    __tablename__ = "workflow_resource"
    __table_args__ = {"schema": "__reana"}

    workflow_id = Column(UUIDType, ForeignKey("__reana.workflow.id_"), primary_key=True)
    resource_id = Column(UUIDType, ForeignKey("__reana.resource.id_"), primary_key=True)
    quantity_used = Column(BigInteger())

    def __repr__(self):
        """Workflow Resource string representation."""
        return "<WorkflowResource {} {}>".format(self.workflow_id, self.resource_id)


class InteractiveSessionResource(Base, Timestamp):
    """Interactive Session Resource table."""

    __tablename__ = "interactive_session_resource"
    __table_args__ = {"schema": "__reana"}

    session_id = Column(
        UUIDType, ForeignKey("__reana.interactive_session.id_"), primary_key=True
    )
    resource_id = Column(UUIDType, ForeignKey("__reana.resource.id_"), primary_key=True)
    quantity_used = Column(BigInteger())

    def __repr__(self):
        """Interactive Session Resource string representation."""
        return "<InteractiveSessionResource {} {}>".format(
            self.session_id, self.resource_id
        )


class QuotaHealth(enum.Enum):
    """Enumeration of quota health statuses."""

    healthy = 0
    warning = 1
    critical = 2
