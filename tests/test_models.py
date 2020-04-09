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

from reana_db.models import (ALLOWED_WORKFLOW_STATUS_TRANSITIONS, Workflow,
                             WorkflowStatus)


def test_workflow_run_number_assignment(db, session):
    """Test workflow run number assignment."""
    workflow_name = 'workflow'
    owner_id = str(uuid4())
    first_workflow = Workflow(
        id_=str(uuid4()),
        name=workflow_name,
        owner_id=owner_id,
        reana_specification=[],
        type_='serial',
        logs='',
    )
    session.add(first_workflow)
    session.commit()
    assert first_workflow.run_number == 1
    second_workflow = Workflow(
        id_=str(uuid4()),
        name=workflow_name,
        owner_id=owner_id,
        reana_specification=[],
        type_='serial',
        logs='',
    )
    session.add(second_workflow)
    session.commit()
    assert second_workflow.run_number == 2
    first_workflow_restart = Workflow(
        id_=str(uuid4()),
        name=workflow_name,
        owner_id=owner_id,
        reana_specification=[],
        type_='serial',
        logs='',
        restart=True,
        run_number=first_workflow.run_number,
    )
    session.add(first_workflow_restart)
    session.commit()
    assert first_workflow_restart.run_number == 1.1
    first_workflow_second_restart = Workflow(
        id_=str(uuid4()),
        name=workflow_name,
        owner_id=owner_id,
        reana_specification=[],
        type_='serial',
        logs='',
        restart=True,
        run_number=first_workflow_restart.run_number,
    )
    session.add(first_workflow_second_restart)
    session.commit()
    assert first_workflow_second_restart.run_number == 1.2


@pytest.mark.parametrize(
    'from_status, to_status, can_transition',
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
    ] + [tuple + (True,) for tuple in ALLOWED_WORKFLOW_STATUS_TRANSITIONS],
)
def test_workflow_can_transition_to(db, session, from_status, to_status,
                                    can_transition):
    """Test workflow run number assignment."""
    workflow_name = 'test-workflow'
    owner_id = str(uuid4())
    workflow = Workflow(
        id_=str(uuid4()),
        name=workflow_name,
        owner_id=owner_id,
        reana_specification=[],
        type_='serial',
        logs='',
        status=from_status
    )
    session.add(workflow)
    session.commit()
    assert workflow.can_transition_to(to_status) is can_transition
