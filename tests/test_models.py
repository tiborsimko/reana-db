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

from reana_db.models import Workflow


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
