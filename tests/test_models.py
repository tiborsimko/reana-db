# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2019 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-DB models tests."""

from uuid import uuid4

import pytest
from mock import patch

from reana_db.config import DEFAULT_QUOTA_RESOURCES
from reana_db.models import (
    ALLOWED_WORKFLOW_STATUS_TRANSITIONS,
    AuditLogAction,
    Resource,
    UserTokenStatus,
    UserTokenType,
    Workflow,
    WorkflowResource,
    RunStatus,
)


def test_workflow_run_number_assignment(db, session, new_user):
    """Test workflow run number assignment."""
    workflow_name = "workflow"

    first_workflow = Workflow(
        id_=str(uuid4()),
        name=workflow_name,
        owner_id=new_user.id_,
        reana_specification=[],
        type_="serial",
        logs="",
    )
    session.add(first_workflow)
    session.commit()
    assert first_workflow.run_number == 1
    second_workflow = Workflow(
        id_=str(uuid4()),
        name=workflow_name,
        owner_id=new_user.id_,
        reana_specification=[],
        type_="serial",
        logs="",
    )
    session.add(second_workflow)
    session.commit()
    assert second_workflow.run_number == 2
    first_workflow_restart = Workflow(
        id_=str(uuid4()),
        name=workflow_name,
        owner_id=new_user.id_,
        reana_specification=[],
        type_="serial",
        logs="",
        restart=True,
        run_number=first_workflow.run_number,
    )
    session.add(first_workflow_restart)
    session.commit()
    assert first_workflow_restart.run_number == 1.1
    first_workflow_second_restart = Workflow(
        id_=str(uuid4()),
        name=workflow_name,
        owner_id=new_user.id_,
        reana_specification=[],
        type_="serial",
        logs="",
        restart=True,
        run_number=first_workflow_restart.run_number,
    )
    session.add(first_workflow_second_restart)
    session.commit()
    assert first_workflow_second_restart.run_number == 1.2


@patch("reana_commons.utils.get_disk_usage", return_value=[{"size": "128"}])
@pytest.mark.parametrize(
    "from_status, to_status, can_transition",
    [
        (RunStatus.created, RunStatus.failed, False),
        (RunStatus.created, RunStatus.finished, False),
        (RunStatus.created, RunStatus.stopped, False),
        (RunStatus.deleted, RunStatus.created, False),
        (RunStatus.deleted, RunStatus.failed, False),
        (RunStatus.deleted, RunStatus.finished, False),
        (RunStatus.deleted, RunStatus.stopped, False),
        (RunStatus.failed, RunStatus.created, False),
        (RunStatus.failed, RunStatus.finished, False),
        (RunStatus.failed, RunStatus.stopped, False),
        (RunStatus.finished, RunStatus.created, False),
        (RunStatus.finished, RunStatus.failed, False),
        (RunStatus.finished, RunStatus.stopped, False),
        (RunStatus.running, RunStatus.created, False),
        (RunStatus.running, RunStatus.deleted, False),
        (RunStatus.stopped, RunStatus.created, False),
        (RunStatus.stopped, RunStatus.failed, False),
        (RunStatus.stopped, RunStatus.finished, False),
        (RunStatus.stopped, RunStatus.running, False),
    ]
    + [tuple + (True,) for tuple in ALLOWED_WORKFLOW_STATUS_TRANSITIONS],
)
def test_workflow_can_transition_to(
    db, session, from_status, to_status, can_transition, new_user
):
    """Test workflow run number assignment."""
    workflow_name = "test-workflow"
    workflow = Workflow(
        id_=str(uuid4()),
        name=workflow_name,
        owner_id=new_user.id_,
        reana_specification=[],
        type_="serial",
        logs="",
        status=from_status,
    )
    session.add(workflow)
    session.commit()
    assert workflow.can_transition_to(to_status) is can_transition


@pytest.mark.parametrize(
    "action, can_do",
    [
        (AuditLogAction.request_token, True),
        ("request_token", True),
        ("delete_database", False),
    ],
)
def test_audit_action(session, new_user, action, can_do):
    """Test audit log actions creation."""
    details = {"reason": "Use REANA."}

    def _audit_action():
        audited_action = new_user.log_action(action, details)
        return audited_action

    if can_do:
        audited_action = _audit_action()
        assert audited_action.action == getattr(
            AuditLogAction, getattr(action, "name", action)
        )
        assert audited_action.details == details
    else:
        with pytest.raises(Exception):
            _audit_action()


def test_access_token(db, session, new_user):
    """Test user access token use cases."""
    assert new_user.access_token
    assert new_user.access_token_status == UserTokenStatus.active.name
    assert new_user.tokens.count() == 1
    assert new_user.active_token.type_ == UserTokenType.reana

    # Assign second active access token
    with pytest.raises(Exception) as e:
        new_user.access_token = "new_token"
    assert "has already an active access token" in e.value.args[0]

    # Revoke token
    new_user.active_token.status = UserTokenStatus.revoked.name
    session.commit()
    assert not new_user.access_token
    assert not new_user.active_token
    assert new_user.access_token_status == UserTokenStatus.revoked.name

    # User requests token
    new_user.request_access_token()
    assert not new_user.access_token
    assert new_user.access_token_status == UserTokenStatus.requested.name

    # Tries to request again
    with pytest.raises(Exception) as e:
        new_user.request_access_token()
    assert "has already requested an access token" in e.value.args[0]

    # Grant new token
    new_user.access_token = "new_token"
    session.commit()
    assert new_user.access_token == "new_token"
    assert new_user.tokens.count() == 2

    # Status of most recent access token
    assert new_user.access_token_status == UserTokenStatus.active.name


@patch("reana_commons.utils.get_disk_usage", return_value=[{"size": "128"}])
def test_workflow_cpu_quota_usage_update(db, session, run_workflow):
    """Test quota usage update once workflow is finished/stopped/failed."""
    time_elapsed_seconds = 0.5
    workflow = run_workflow(time_elapsed_seconds=time_elapsed_seconds)
    cpu_resource = Resource.query.filter_by(
        name=DEFAULT_QUOTA_RESOURCES["cpu"]
    ).one_or_none()
    cpu_milliseconds = (
        WorkflowResource.query.filter_by(
            workflow_id=workflow.id_, resource_id=cpu_resource.id_
        )
        .first()
        .quantity_used
    )
    assert cpu_milliseconds >= time_elapsed_seconds * 1000


@patch("reana_commons.utils.get_disk_usage", return_value=[{"size": "128"}])
def test_user_cpu_usage(db, session, new_user, run_workflow):
    """Test aggregated CPU usage per user."""
    time_elapsed_seconds = 0.5
    num_workflows = 2
    for n in range(num_workflows):
        run_workflow(time_elapsed_seconds=time_elapsed_seconds)

    assert (
        new_user.get_quota_usage()["cpu"]["usage"]
        >= num_workflows * time_elapsed_seconds * 1000
    )
    assert new_user.get_quota_usage()["disk"]["usage"] == 128
