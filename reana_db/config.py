# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA DB configuration."""

import os

from reana_commons.config import REANA_INFRASTRUCTURE_COMPONENTS_HOSTNAMES

DB_NAME = os.getenv("REANA_DB_NAME", "reana")
"""Database name."""

DB_USERNAME = os.getenv("REANA_DB_USERNAME", "reana")
"""Database user name."""

DB_PASSWORD = os.getenv("REANA_DB_PASSWORD", "reana")
"""Database password."""

DB_HOST = REANA_INFRASTRUCTURE_COMPONENTS_HOSTNAMES["db"]
"""Database service host."""
# Loading REANA_COMPONENT_PREFIX from environment because REANA-DB
# doesn't depend on REANA-Commons, the package which loads this config.

DB_PORT = os.getenv("REANA_DB_PORT", "5432")
"""Database service port."""

DB_SECRET_KEY = os.getenv("REANA_SECRET_KEY", "reana")
"""Database encryption secret key."""

SQLALCHEMY_DATABASE_URI = os.getenv(
    "REANA_SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://{username}:{password}"
    "@{host}:{port}/{db}".format(
        username=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        db=DB_NAME,
    ),
)
"""SQLAlchemy database location."""
