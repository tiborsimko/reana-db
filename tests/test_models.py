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
import mock

from reana_db.models import (
    ALLOWED_WORKFLOW_STATUS_TRANSITIONS,
    AuditLogAction,
    JobStatus,
    UserTokenStatus,
    UserTokenType,
    Workflow,
    WorkflowStatus,
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


@pytest.mark.parametrize(
    "from_status, to_status, can_transition",
    [
        (WorkflowStatus.created, WorkflowStatus.failed, False),
        (WorkflowStatus.created, WorkflowStatus.finished, False),
        (WorkflowStatus.created, WorkflowStatus.stopped, False),
        (WorkflowStatus.deleted, WorkflowStatus.created, False),
        (WorkflowStatus.deleted, WorkflowStatus.failed, False),
        (WorkflowStatus.deleted, WorkflowStatus.finished, False),
        (WorkflowStatus.deleted, WorkflowStatus.stopped, False),
        (WorkflowStatus.failed, WorkflowStatus.created, False),
        (WorkflowStatus.failed, WorkflowStatus.finished, False),
        (WorkflowStatus.failed, WorkflowStatus.stopped, False),
        (WorkflowStatus.finished, WorkflowStatus.created, False),
        (WorkflowStatus.finished, WorkflowStatus.failed, False),
        (WorkflowStatus.finished, WorkflowStatus.stopped, False),
        (WorkflowStatus.running, WorkflowStatus.created, False),
        (WorkflowStatus.running, WorkflowStatus.deleted, False),
        (WorkflowStatus.stopped, WorkflowStatus.created, False),
        (WorkflowStatus.stopped, WorkflowStatus.failed, False),
        (WorkflowStatus.stopped, WorkflowStatus.finished, False),
        (WorkflowStatus.stopped, WorkflowStatus.running, False),
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


@pytest.mark.parametrize(
    "REANA_RUNTIME_KUBERNETES_KEEP_ALIVE_JOBS_WITH_STATUSES, job_status, should_cleanup, class_, emits_warning",
    [
        (["failed", "finished"], WorkflowStatus.finished, False, WorkflowStatus, False),
        (["failed"], WorkflowStatus.finished, True, WorkflowStatus, False),
        (["failed"], "finished", True, WorkflowStatus, False),
        (["failed", "finished"], JobStatus.finished, False, JobStatus, False),
        (["failed"], JobStatus.failed, False, JobStatus, False),
        (["failed"], "failed", False, JobStatus, False),
        (["faild"], "failed", True, JobStatus, True),
        ([], "failed", True, JobStatus, False),
    ],
)
def test_should_cleanup_job(
    REANA_RUNTIME_KUBERNETES_KEEP_ALIVE_JOBS_WITH_STATUSES,
    job_status,
    should_cleanup,
    class_,
    emits_warning,
    caplog,
):
    """Test logic to determine whether jobs should be cleaned up depending on their status."""
    with mock.patch(
        "reana_db.models.REANA_RUNTIME_KUBERNETES_KEEP_ALIVE_JOBS_WITH_STATUSES",
        REANA_RUNTIME_KUBERNETES_KEEP_ALIVE_JOBS_WITH_STATUSES,
    ):
        assert class_.should_cleanup_job(job_status) == should_cleanup
        if emits_warning:
            assert any(
                s in caplog.text
                for s in REANA_RUNTIME_KUBERNETES_KEEP_ALIVE_JOBS_WITH_STATUSES
            )
