# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2020 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA DB command line."""

import os
import sys

import click
from alembic import command
from alembic import config as alembic_config
from reana_db.database import init_db
from reana_db.models import Resource
from reana_db.utils import update_users_disk_quota


@click.group()
def cli():
    """REANA database commands."""


@cli.command()
def init():
    """Show REANA database migration recipes history."""
    init_db()
    click.secho("Database initialised.", fg="green")


@cli.group("alembic")
@click.pass_context
def alembic_group(ctx):
    """REANA database migration commands.

    Note that this command is just a light wrapper around alembic.
    """
    reana_alembic_ini = os.path.join(os.path.dirname(__file__), "alembic.ini")
    config = alembic_config.Config(reana_alembic_ini)
    ctx.obj = config


@alembic_group.command(name="init")
@click.pass_obj
def alembic_init(config):
    """Populate 'alembic_version' table with existing revisions."""
    command.stamp(config, "head")


@alembic_group.command()
@click.option(
    "-m", "--message", default=None, help="Message string to use with 'revision'"
)
@click.option(
    "--autogenerate/--no-autogenerate",
    default=True,
    help=(
        "Populate revision script with candidate "
        "migration operations, based on comparison of "
        "database to model"
    ),
)
@click.option(
    "--sql",
    default=False,
    help=(
        "Don't emit SQL to database - dump to standard output/file instead. See alembic docs on offline mode."
    ),
)
@click.option(
    "--head",
    default="head",
    help=("Specify head revision or <branchname>@head to base new revision on."),
)
@click.option(
    "--splice",
    is_flag=True,
    help=("Allow a non-head revision as the 'head' to splice onto."),
)
@click.option(
    "--branch-label",
    default=None,
    help=("Specify a branch label to apply to the new revision"),
)
@click.option(
    "--version-path",
    default=None,
    help=("Specify specific path from config for version file"),
)
@click.option(
    "--rev-id",
    default=None,
    help=("Specify a hardcoded revision id instead of generating one"),
)
@click.option(
    "--depends-on",
    default=None,
    help=(
        "Specify one or more revision identifiers which this revision should depend on."
    ),
)
@click.pass_obj
def revision(
    config,
    message,
    autogenerate,
    sql,
    head,
    splice,
    branch_label,
    version_path,
    rev_id,
    depends_on,
):
    """Create a REANA database alembic revision."""
    command.revision(
        config,
        message=message,
        autogenerate=autogenerate,
        sql=sql,
        head=head,
        splice=splice,
        branch_label=branch_label,
        version_path=version_path,
        rev_id=rev_id,
        depends_on=depends_on,
    )


@alembic_group.command()
@click.argument("revision", default="head")
@click.option(
    "--sql",
    is_flag=True,
    help=(
        "Don't emit SQL to database - dump to standard output/file instead. See alembic docs on offline mode."
    ),
)
@click.option(
    "--tag",
    default=None,
    help=("Arbitrary 'tag' name - can be used by custom env.py scripts."),
)
@click.pass_obj
def upgrade(config, revision, sql, tag):
    """Upgrade REANA database."""
    command.upgrade(config, revision, sql=sql, tag=tag)


@alembic_group.command()
@click.argument("revision", default="head")
@click.option(
    "--sql",
    is_flag=True,
    help=(
        "Don't emit SQL to database - dump to standard output/file instead. See alembic docs on offline mode."
    ),
)
@click.option(
    "--tag",
    default=None,
    help=("Arbitrary 'tag' name - can be used by custom env.py scripts."),
)
@click.pass_obj
def downgrade(config, revision, sql, tag):
    """Downgrade REANA database."""
    command.downgrade(config, revision, sql=sql, tag=tag)


@alembic_group.command()
@click.option(
    "-v", "--verbose", is_flag=True, help=("Use more verbose output."),
)
@click.pass_obj
def current(config, verbose):
    """Show current database state."""
    command.current(config, verbose=verbose)


@alembic_group.command()
@click.option(
    "-r",
    "--rev-range",
    default=None,
    help=("Specify a revision range; format is [start]:[end]."),
)
@click.option(
    "-v", "--verbose", is_flag=True, help=("Use more verbose output."),
)
@click.option(
    "-i", "--indicate-current", is_flag=True, help=("Indicate the current revision."),
)
@click.pass_obj
def history(config, rev_range, verbose, indicate_current):
    """Show REANA database migration recipes history."""
    command.history(
        config, rev_range=rev_range, verbose=verbose, indicate_current=indicate_current
    )


@cli.group("quota")
@click.pass_context
def quota_group(ctx):
    """REANA DB quota related commands."""


@quota_group.command()
def create_default_resources():
    """Create default quota resources."""
    created_resources = Resource.initialise_default_resources()
    if created_resources:
        click.secho(
            "Created resources: {}".format([r.name for r in created_resources]),
            fg="green",
        )
    else:
        click.secho(
            "No action to be taken: default resources already exist.", fg="yellow"
        )
        sys.exit(1)


@quota_group.command()
def disk_usage_update():
    """Update users disk quota usage based on user workspace."""
    try:
        update_users_disk_quota()
        click.secho("Users disk quota usage updated successfully.", fg="green")
    except Exception as e:
        click.secho(
            "[ERROR]: An error occurred when updating users disk quota usage: {}".format(
                repr(e)
            ),
            fg="red",
        )
        sys.exit(1)
