# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Sample conditions used by REANA scheduler tests."""


def sample_condition_for_starting_queued_workflows():
    """Sample always true condition."""
    return True


def sample_condition_for_requeueing_workflows():
    """Sample always false condition."""
    return False
