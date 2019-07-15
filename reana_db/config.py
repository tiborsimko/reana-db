# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA DB configuration."""

import os

DB_NAME = os.getenv('REANA_DB_NAME', 'reana')
"""Database name."""

DB_USERNAME = os.getenv('REANA_DB_USERNAME', 'reana')
"""Database user name."""

DB_PASSWORD = os.getenv('REANA_DB_PASSWORD', 'reana')
"""Database password."""

DB_HOST = os.getenv('REANA_DB_HOST', 'db')
"""Database service host."""

DB_PORT = os.getenv('REANA_DB_PORT', '5432')
"""Database service port."""

SQLALCHEMY_DATABASE_URI = \
    os.getenv(
        'REANA_SQLALCHEMY_DATABASE_URI',
        'postgresql+psycopg2://{username}:{password}'
        '@{host}:{port}/{db}'.format(
            username=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST,
            port=DB_PORT, db=DB_NAME
        ))
"""SQLAlchemy database location."""
