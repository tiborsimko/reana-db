# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA DB configuration."""

import os

SQLALCHEMY_DATABASE_URI = \
    os.getenv('REANA_SQLALCHEMY_DATABASE_URI',
              'postgresql+psycopg2://reana:reana@db:5432/reana')
"""SQLAlchemy database location."""
