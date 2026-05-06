# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest plugin entry point for REANA-DB fixtures.

Only the database-coupled fixtures live here. Pure-Python and
REANA-Commons-coupled fixtures (workflow spec dicts, queue helpers,
workspace fixtures) are provided by ``reana_commons.testing.plugin``,
which pytest auto-loads independently because ``reana-db[tests]``
declares ``reana-commons[tests]`` as a dependency.
"""

from __future__ import absolute_import, print_function

from .fixtures import (  # noqa: F401
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
