# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-DB config tests."""

import importlib

import pytest

import reana_db.config as config


def test_periodic_quota_config_is_loaded_from_environment(monkeypatch):
    """Test periodic quota defaults are parsed from environment variables."""
    with monkeypatch.context() as context:
        context.setenv("REANA_DEFAULT_QUOTA_CPU_PERIOD_RESET_MONTHS", "6")
        context.setenv("REANA_PERIODIC_RESOURCE_QUOTA_UPDATE_POLICY", "true")

        reloaded_config = importlib.reload(config)

        assert reloaded_config.DEFAULT_QUOTA_CPU_PERIOD_RESET_MONTHS == 6
        assert bool(reloaded_config.PERIODIC_RESOURCE_QUOTA_UPDATE_POLICY) is True
        assert (
            reloaded_config._get_optional_period_months_env(
                "REANA_DEFAULT_QUOTA_CPU_PERIOD_RESET_MONTHS"
            )
            == 6
        )

    importlib.reload(config)


@pytest.mark.parametrize("disabled_value", ["", "0"])
def test_periodic_quota_config_uses_none_for_disabled_months(
    monkeypatch, disabled_value
):
    """Test missing or zero periodic quota month configuration disables it."""
    with monkeypatch.context() as context:
        context.setenv("REANA_DEFAULT_QUOTA_CPU_PERIOD_RESET_MONTHS", disabled_value)
        context.setenv("REANA_PERIODIC_RESOURCE_QUOTA_UPDATE_POLICY", "false")

        reloaded_config = importlib.reload(config)

        assert reloaded_config.DEFAULT_QUOTA_CPU_PERIOD_RESET_MONTHS is None
        assert bool(reloaded_config.PERIODIC_RESOURCE_QUOTA_UPDATE_POLICY) is False
        assert (
            reloaded_config._get_optional_period_months_env(
                "REANA_DEFAULT_QUOTA_CPU_PERIOD_RESET_MONTHS"
            )
            is None
        )

    importlib.reload(config)


def test_periodic_quota_config_rejects_negative_or_decimal_months(monkeypatch):
    """Test invalid periodic quota month values fail fast at config load time."""
    for invalid_value in ("-3", "3.9"):
        with monkeypatch.context() as context:
            context.setenv("REANA_DEFAULT_QUOTA_CPU_PERIOD_RESET_MONTHS", invalid_value)

            with pytest.raises(ValueError):
                importlib.reload(config)

    importlib.reload(config)
