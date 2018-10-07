# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""REANA-DB utils."""

import os


def build_workspace_path(user_id, workflow_id=None):
    """Build user's workspace relative path.

    :param user_id: Owner of the workspace.
    :param workflow_id: Optional parameter, if provided gives the path to the
        workflow workspace instead of just the path to the user workspace.
    :return: String that represents the workspace the OS independent path.
        i.e. users/0000/workflows/0034
    """
    workspace_path = os.path.join('users', str(user_id), 'workflows')
    if workflow_id:
        workspace_path = os.path.join(workspace_path, str(workflow_id))

    return workspace_path
