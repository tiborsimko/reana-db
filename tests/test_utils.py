# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2019 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-DB utils tests."""

from __future__ import absolute_import, print_function

import os

from reana_commons.config import SHARED_VOLUME_PATH


def test_build_workspace_path():
    """Tests for build_workspace_path()."""
    from reana_db.utils import build_workspace_path

    assert build_workspace_path(0) == os.path.join(
        SHARED_VOLUME_PATH, "users/0/workflows"
    )
