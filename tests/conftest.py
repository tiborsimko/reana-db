# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration for REANA-DB."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from reana_db.models import Base


@pytest.fixture(scope="module")
def db():
    """Flask application fixture."""
    test_db_engine = create_engine('sqlite:///testdb.db')
    if not database_exists(test_db_engine.url):
        create_database(test_db_engine.url)
    Base.metadata.create_all(bind=test_db_engine)
    yield test_db_engine
    drop_database(test_db_engine.url)


@pytest.fixture()
def session(db):
    """Create a SQL Alchemy session.

    Scope: function

    This fixture offers a SQLAlchemy session which has been created from the
    ``db_engine`` fixture.

    .. code-block:: python

        from reana_db.models import Workflow

        def test_create_workflow(session):
            workflow = Workflow(...)
            session.add(workflow)
            session.commit()
    """
    Session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=db))
    Base.query = Session.query_property()
    from reana_db.database import Session as _Session
    _Session.configure(bind=db)
    yield Session
    Session.close()
