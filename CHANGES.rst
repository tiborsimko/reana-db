Changes
=======

Version 0.9.0 (UNRELEASED)
---------------------------

- Adds new ``launcher_url`` column to the ``Workflow`` table to store the remote origin of workflows submitted via Launch on REANA.
- Adds new ``WorkspaceRetentionRule`` table to store workspace file retention rules.
- Adds a limit to the number of times a workflow can be restarted.
- Adds new ``pending`` status to ``WorkspaceRetentionRuleStatus``.
- Changes percentage ranges for calculating the quota health status.
- Changes ``Workflow.get_workspace_disk_usage`` to calculate disk usage and not use the usage values from database.
- Changes to PostgreSQL 12.10.

Version 0.8.2 (2022-02-23)
---------------------------

- Adds transition for workflow from queued to failed status.

Version 0.8.1 (2022-02-01)
---------------------------

- Adds an option to periodically calculate CPU quota usage.
- Changes CLI quota command from ``disk-usage-update`` to ``resource-usage-update`` since it can also perform CPU quota calculation.
- Fixes quota update functions to handle exceptional situation as continuable errors.
- Removes extra ``QuotaResourceType`` enum in favor of ``ResourceType.name``.

Version 0.8.0 (2021-11-22)
---------------------------

- Adds new disk usage retrieval methods using canonical (bytes) and human-readable (KiB) units. (``User``, ``Workflow``)
- Adds Quota models which calculates CPU and disk usage.
- Adds ``InteractiveSession`` model.
- Adds new properties ``started_at`` and ``finished_at`` to the ``Job`` model, updated on status change.
- Adds ``get_priority`` workflow method, that combines both complexity and concurrency, to pass to the scheduler.
- Adds a possibility to configure database connection pool parameters via environment variables.
- Adds new ``pending`` state to ``RunStatus`` table.
- Adds workflow complexity property in ``Workflow`` table.
- Adds environment variable to configure which quotas to update.
- Changes ``WorkflowStatus`` table to ``RunStatus``.
- Changes disk quota calculation functions to allow passing raw bytes to increase the used quota.
- Changes to PostgreSQL 12.8.
- Removes support for Python 2.

Version 0.7.3 (2021-03-17)
--------------------------

- Fixes REANA installation by pinning SQLAlchemy version less than 1.4.0 due to https://github.com/kvesteri/sqlalchemy-utils/issues/505.

Version 0.7.2 (2021-02-22)
--------------------------

- Adds utility to status enums to decide whether to clean workflows and jobs depending on their status.

Version 0.7.1 (2021-02-02)
--------------------------

- Adds support for Python 3.9.
- Fixes minor code warnings.
- Changes CI system to include Python flake8 checker.

Version 0.7.0 (2020-10-20)
--------------------------

- Adds initial central workflow status transition logic handler.
- Adds new audit table and logic to register actions. (``AuditLog``, ``AuditLogAction``)
- Adds fixtures for better testing of database models.
- Changes user token storage to move tokens from ``User`` table to ``UserToken`` table and to encrypt them.
- Changes ``Workflow`` table to add a new ``workspace_path`` column.
- Changes default database service to use centrally configured one from REANA-Commons. (``REANA_INFRASTRUCTURE_COMPONENTS_HOSTNAMES``)
- Changes code formatting to respect ``black`` coding style.
- Changes documentation to single-page layout.

Version 0.6.0 (2019-12-19)
--------------------------

- Adds new method which returns full workflow name.
- Adds more granular DB configuration.
- Adds Git repository information to the workflow model.
  (``Workflow.git_repo``, ``Workflow.git_provider``)
- Adds user name information to the user model.
  (``User.full_name``, ``User.username``)
- Removes restart count information from the job model.
  (``Job.restart_count``, ``Job.max_restart_count``)
- Adds support for Python 3.8.

Version 0.5.0 (2019-04-16)
--------------------------

- Introduces new workflow statuses: ``deleted``, ``stopped``, ``queued``.
- Adds new field to store workflow stopping time. (``Workflow.run_stopped_at``)
- Moves workflow input parameters to its own column to separate them from
  operational options. Adapts getters accordingly.
  (``Workflow.input_parameters``)
- Adds new method to retrieve the workflow owner's token.
  (``Workflow.get_owner_access_token``)
- Introduces new utility function to retrieve workflows by ``uuid`` or name.
  (``_get_workflow_with_uuid_or_name``)
- Introduces new fields for interactive sessions: ``interactive_session``,
  ``interactive_session_name`` and ``interactive_session_type``. Note that with
  current design only one interactive session per workflow is supported.
- Adds a new enumeration for possible job statuses. (``JobStatus``)
- Adds new field to identify jobs in the underlying compute backend.
  (``Job.backend_job_id``)

Version 0.4.0 (2018-11-06)
--------------------------

- Stores ``reana.yaml`` in database models.
- Adds Workflow specification and parameter getters.
- Adds support for Python 3.7.
- Changes license to MIT.

Version 0.3.0 (2018-08-10)
--------------------------

- This package is a result of refactoring `reana-commons
  <https://reana-commons.readthedocs.io/>`_.
- Provides common REANA models.
- Provides database connection logic.

.. admonition:: Please beware

   Please note that REANA is in an early alpha stage of its development. The
   developer preview releases are meant for early adopters and testers. Please
   don't rely on released versions for any production purposes yet.
