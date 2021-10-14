# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2019, 2021 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-DB utils tests."""

from __future__ import absolute_import, print_function

import pytest

from reana_commons.config import SHARED_VOLUME_PATH


@pytest.mark.parametrize(
    "user_id,workflow_id,workspace_root_path,workspace_path",
    [
        (0, None, None, SHARED_VOLUME_PATH + "/users/0/workflows"),
        (0, 1, None, SHARED_VOLUME_PATH + "/users/0/workflows/1"),
        (0, 1, "/eos/myanalysis", "/eos/myanalysis/1"),
        (0, 1, SHARED_VOLUME_PATH, SHARED_VOLUME_PATH + "/users/0/workflows/1"),
        (0, 1, SHARED_VOLUME_PATH + "/db", SHARED_VOLUME_PATH + "/users/0/workflows/1"),
    ],
)
def test_build_workspace_path(
    user_id, workflow_id, workspace_root_path, workspace_path
):

    """Tests for build_workspace_path()."""
    from reana_db.utils import build_workspace_path

    assert (
        build_workspace_path(
            user_id=user_id,
            workflow_id=workflow_id,
            workspace_root_path=workspace_root_path,
        )
        == workspace_path
    )
