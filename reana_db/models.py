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
import uuid
from datetime import datetime

from reana_commons.utils import get_disk_usage
from reana_db.config import DB_SECRET_KEY, DEFAULT_QUOTA_RESOURCES
from reana_db.utils import build_workspace_path
from requests.sessions import session
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

    def get_user_disk_usage(self, block_size=None):
        """Retrieve user disk usage information."""
        try:
            workspace_path = self.get_user_workspace()
            disk_usage = get_disk_usage(workspace_path, True, block_size)
            return disk_usage[0]["size"]
        except Exception:
            return -1

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
        for user_resource in self.resources:
            if user_resource.resource.type_ == resource_type:
                quota_usage += user_resource.quota_used
                quota_limit += user_resource.quota_limit

        return {
            "usage": quota_usage,
            "limit": quota_limit,
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
                    quota_limit=0,
                    quota_used=0,
                )
            )

    def get_quota_usage(self):
        """Get user quota usage information."""
        return dict(
            disk=dict(
                usage=self.get_user_disk_usage(),
                limit=self.get_user_quota_by_type(ResourceType.disk)["limit"],
                health=self.get_user_quota_by_type(ResourceType.disk)["health"],
            ),
            cpu=self.get_user_quota_by_type(ResourceType.cpu),
        )

    def __repr__(self):
        """User string represetantion."""
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


class WorkflowStatus(enum.Enum):
    """Enumeration of possible workflow statuses."""

    created = 0
    running = 1
    finished = 2
    failed = 3
    deleted = 4
    stopped = 5
    queued = 6


ALLOWED_WORKFLOW_STATUS_TRANSITIONS = [
    # Creation
    (WorkflowStatus.created, WorkflowStatus.deleted),
    (WorkflowStatus.created, WorkflowStatus.running),
    # Running
    (WorkflowStatus.running, WorkflowStatus.failed),
    (WorkflowStatus.running, WorkflowStatus.finished),
    (WorkflowStatus.running, WorkflowStatus.stopped),
    (WorkflowStatus.running, WorkflowStatus.running),
    # Stopped
    (WorkflowStatus.stopped, WorkflowStatus.deleted),
    # Failed
    (WorkflowStatus.failed, WorkflowStatus.deleted),
    (WorkflowStatus.failed, WorkflowStatus.running),
    # Finished
    (WorkflowStatus.finished, WorkflowStatus.deleted),
    (WorkflowStatus.finished, WorkflowStatus.running),
]


class JobStatus(enum.Enum):
    """Enumeration of possible job statuses."""

    created = 0
    running = 1
    finished = 2
    failed = 3
    stopped = 4
    queued = 5


class Workflow(Base, Timestamp):
    """Workflow table."""

    __tablename__ = "workflow"

    id_ = Column(UUIDType, primary_key=True)
    name = Column(String(255))
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.created)
    owner_id = Column(UUIDType, ForeignKey("__reana.user_.id_"))
    reana_specification = Column(JSONType)
    input_parameters = Column(JSONType)
    operational_options = Column(JSONType)
    type_ = Column(String(30))
    interactive_session = Column(Text)
    interactive_session_name = Column(Text)
    interactive_session_type = Column(Text)
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
        interactive_session=None,
        interactive_session_name=None,
        interactive_session_type=None,
        input_parameters={},
        operational_options={},
        status=WorkflowStatus.created,
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
        self.interactive_session = interactive_session
        self.interactive_session_name = interactive_session_name
        self.interactive_session_type = interactive_session_type
        self.git_ref = git_ref
        self.git_repo = git_repo
        self.git_provider = git_provider
        self.restart = restart
        self._run_number = self.assign_run_number(run_number)
        self.workspace_path = workspace_path or build_workspace_path(
            self.owner_id, self.id_
        )

    def __repr__(self):
        """Workflow string represetantion."""
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
        return get_disk_usage(self.workspace_path, summarize, block_size)

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


@event.listens_for(Workflow.status, "set")
def workflow_status_change_listener(workflow, new_status, old_status, initiator):
    """Workflow status change listener."""
    if new_status in [
        WorkflowStatus.finished,
        WorkflowStatus.failed,
    ]:
        workflow.run_finished_at = datetime.now()
    elif new_status in [WorkflowStatus.stopped]:
        workflow.run_stopped_at = datetime.now()
    elif new_status in [WorkflowStatus.running]:
        workflow.run_started_at = datetime.now()

    finished_at = workflow.run_finished_at or workflow.run_stopped_at
    if workflow.run_started_at and finished_at:
        cpu_time = finished_at - workflow.run_started_at
        cpu_milliseconds = int(cpu_time.total_seconds() * 1000)
        cpu_resource = Resource.query.filter_by(
            name=DEFAULT_QUOTA_RESOURCES["cpu"]
        ).one_or_none()
        if cpu_resource:
            from .database import Session

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
                        title=f"Default {type_} resource.",
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


class QuotaHealth(enum.Enum):
    """Enumeration of quota health statuses."""

    healthy = 0
    warning = 1
    critical = 2
