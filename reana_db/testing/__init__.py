# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest fixtures and helpers for REANA-DB.

Database-coupled fixtures previously living in ``pytest-reana`` are exposed
from this subpackage. It is registered as a pytest plugin via the
``pytest11`` entry point, so projects that install ``reana-db[tests]`` get
the fixtures auto-loaded by pytest collection.
"""

from __future__ import absolute_import, print_function

from .conditions import (
    sample_condition_for_requeueing_workflows,
    sample_condition_for_starting_queued_workflows,
)
from .fixtures import (
    app,
    sample_serial_workflow_in_db,
    sample_serial_workflow_in_db_owned_by_user1,
    sample_yadage_workflow_in_db,
    sample_yadage_workflow_in_db_owned_by_user1,
    session,
    user0,
    user1,
    user2,
)

__all__ = (
    "app",
    "sample_condition_for_requeueing_workflows",
    "sample_condition_for_starting_queued_workflows",
    "sample_serial_workflow_in_db",
    "sample_serial_workflow_in_db_owned_by_user1",
    "sample_yadage_workflow_in_db",
    "sample_yadage_workflow_in_db_owned_by_user1",
    "session",
    "user0",
    "user1",
    "user2",
)
