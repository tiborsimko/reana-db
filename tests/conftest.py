# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration for REANA-DB."""


from uuid import uuid4

import pytest

from reana_db.models import User


@pytest.fixture(scope="module")
def db():
    """Initialize database fixture."""
    from reana_db.database import init_db

    init_db()


@pytest.fixture
def new_user(session):
    """Create new user."""
    user = User(
        email="{}@reana.io".format(uuid4()), access_token="secretkey-{}".format(uuid4())
    )
    session.add(user)
    session.commit()
    return user
