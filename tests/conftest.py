# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration for REANA-DB."""


from datetime import datetime
from time import sleep
from uuid import uuid4

import pytest

from reana_db.config import DEFAULT_QUOTA_RESOURCES
from reana_db.models import (
    Resource,
    ResourceType,
    ResourceUnit,
    User,
    UserResource,
    Workflow,
    WorkflowStatus,
)


@pytest.fixture(scope="module")
def db():
    """Initialize database fixture."""
    from reana_db.database import init_db

    init_db()
    Resource.initialise_default_resources()


@pytest.fixture
def new_user(session):
    """Create new user."""
    user = User(
        email="{}@reana.io".format(uuid4()), access_token="secretkey-{}".format(uuid4())
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def run_workflow(session, new_user):
    """Mocked workflow run factory."""

    def _run_workflow(time_elapsed_seconds=0.5):
        """Mock a workflow run."""
        now = datetime.now()
        id_ = uuid4()
        workflow = Workflow(
            id_=str(id_),
            name=f"test_{id_}",
            owner_id=new_user.id_,
            reana_specification=[],
            type_="serial",
            logs="",
            status=WorkflowStatus.created,
        )
        # start workflow
        workflow.status = WorkflowStatus.running
        session.add(workflow)
        session.commit()
        # simulate time elapsed
        sleep(time_elapsed_seconds)
        Workflow.update_workflow_status(session, workflow.id_, WorkflowStatus.finished)
        return workflow

    return _run_workflow
