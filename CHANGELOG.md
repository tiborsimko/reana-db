# Changelog

## [0.95.0](https://github.com/tiborsimko/reana-db/compare/v0.9.5...0.95.0) (2026-02-10)


### ⚠ BREAKING CHANGES

* **python:** drop support for Python 3.6 and 3.7

### Build

* **python:** add minimal `pyproject.toml` ([#237](https://github.com/tiborsimko/reana-db/issues/237)) ([de1e03b](https://github.com/tiborsimko/reana-db/commit/de1e03b7f81fd1a49b9c2abdc7c5b6d164fe1f37))
* **python:** add support for SQLAlchemy 1.4 ([#234](https://github.com/tiborsimko/reana-db/issues/234)) ([f341b21](https://github.com/tiborsimko/reana-db/commit/f341b21f203225f9537073fe67ec42578db11f02)), closes [#228](https://github.com/tiborsimko/reana-db/issues/228)
* **python:** drop support for Python 3.6 and 3.7 ([#235](https://github.com/tiborsimko/reana-db/issues/235)) ([16448cd](https://github.com/tiborsimko/reana-db/commit/16448cd8e319661ce73697e6c66d138e0728b228))
* **python:** remove deprecated `pytest-runner` ([#237](https://github.com/tiborsimko/reana-db/issues/237)) ([09f2df8](https://github.com/tiborsimko/reana-db/commit/09f2df890be324841f3842cc73c8554b6be969a3))
* **python:** use optional deps instead of `tests_require` ([#237](https://github.com/tiborsimko/reana-db/issues/237)) ([18302ea](https://github.com/tiborsimko/reana-db/commit/18302ea372e76f6c05e65625f921902cbfb51710))


### Features

* **cli:** add new `migrate-secret-key` command ([#240](https://github.com/tiborsimko/reana-db/issues/240)) ([efcbe72](https://github.com/tiborsimko/reana-db/commit/efcbe724a2797edf94a531a2fd49ae0dc25d29f7))
* **models:** add service tables ([#241](https://github.com/tiborsimko/reana-db/issues/241)) ([f573cbd](https://github.com/tiborsimko/reana-db/commit/f573cbdf17fae20e8225a30726333931565fe670))
* **models:** add ServiceLogs table ([#248](https://github.com/tiborsimko/reana-db/issues/248)) ([8bfc203](https://github.com/tiborsimko/reana-db/commit/8bfc203028d3b3d9af191f5a064312aaa65ba0b7))
* **models:** add workflow run sharing tables ([#216](https://github.com/tiborsimko/reana-db/issues/216)) ([4b78d63](https://github.com/tiborsimko/reana-db/commit/4b78d6365eabb4d168eed2d44e060baf37217fcf)), closes [#206](https://github.com/tiborsimko/reana-db/issues/206)
* **utils:** add `include_shared_workflows` parameter ([#216](https://github.com/tiborsimko/reana-db/issues/216)) ([0f3c091](https://github.com/tiborsimko/reana-db/commit/0f3c0918f39dfb76dc6961a3c356557107c5b9f0))


### Bug fixes

* **models:** add missing foreign key to workflow_uuid of Job ([#214](https://github.com/tiborsimko/reana-db/issues/214)) ([5b41246](https://github.com/tiborsimko/reana-db/commit/5b41246e686b68d7b58295070fe08d1e6a0ed3fe)), closes [#210](https://github.com/tiborsimko/reana-db/issues/210)
* **models:** remove duplicated User-Workflow relationship ([#234](https://github.com/tiborsimko/reana-db/issues/234)) ([a364bb0](https://github.com/tiborsimko/reana-db/commit/a364bb0a5db5bedf5c00b21e437ea8da1abd62df))


### Code refactoring

* **docs:** move from reST to Markdown ([#225](https://github.com/tiborsimko/reana-db/issues/225)) ([b48eb55](https://github.com/tiborsimko/reana-db/commit/b48eb55f7a1b1bbdde0e0a458852349a439a511e))


### Code style

* **black:** format with black v24 ([#224](https://github.com/tiborsimko/reana-db/issues/224)) ([cc60522](https://github.com/tiborsimko/reana-db/commit/cc6052242fd14cf3413b793d0aa32a24871fe1b1))
* **python:** adapt code base to the new black version ([#253](https://github.com/tiborsimko/reana-db/issues/253)) ([6f1e3c1](https://github.com/tiborsimko/reana-db/commit/6f1e3c1f5fed6be5a975fceae4c6c8420c30a129))


### Continuous integration

* **actions:** pin setuptools 70 ([#239](https://github.com/tiborsimko/reana-db/issues/239)) ([3202759](https://github.com/tiborsimko/reana-db/commit/320275969c64513f695ce59a145088f6222aa594))
* **actions:** update GitHub actions due to Node 16 deprecation ([#233](https://github.com/tiborsimko/reana-db/issues/233)) ([f418dfb](https://github.com/tiborsimko/reana-db/commit/f418dfba0b5b9c49039e7f64944104ed4685b78c))
* **actions:** upgrade to Ubuntu 24.04 and Python 3.12 ([#236](https://github.com/tiborsimko/reana-db/issues/236)) ([f37e58e](https://github.com/tiborsimko/reana-db/commit/f37e58e98853670fe29bebbde4046d3b9bf6bf21))
* added flake8 linter ([5f5c3a2](https://github.com/tiborsimko/reana-db/commit/5f5c3a2a4a0daa5b874f41c1becff7a38bbe9b6e))
* added github actions workflow ([f2b4dfa](https://github.com/tiborsimko/reana-db/commit/f2b4dfa8405a0362fa3cbab05a5e65a6ecee6671))
* added python 2.7 to github action python test strategy ([11faa73](https://github.com/tiborsimko/reana-db/commit/11faa7345d6b41068391dd30e2b07a76823aee39)), closes [#107](https://github.com/tiborsimko/reana-db/issues/107)
* adopted db models to work with python 2.7 ([63cb814](https://github.com/tiborsimko/reana-db/commit/63cb814b1867bf3ec8056fc8f8b24179ead0b67a)), closes [#107](https://github.com/tiborsimko/reana-db/issues/107)
* **commitlint:** addition of commit message linter ([#218](https://github.com/tiborsimko/reana-db/issues/218)) ([ee0f7e5](https://github.com/tiborsimko/reana-db/commit/ee0f7e5e106e0be619779bfa2133415feecc323b))
* **commitlint:** allow release commit style ([#229](https://github.com/tiborsimko/reana-db/issues/229)) ([adf15d7](https://github.com/tiborsimko/reana-db/commit/adf15d7c6457eddadc3da1aa8b95b74cfc1239fb))
* **commitlint:** check for the presence of concrete PR number ([#223](https://github.com/tiborsimko/reana-db/issues/223)) ([3d513f6](https://github.com/tiborsimko/reana-db/commit/3d513f6cda44e9e40b3c8f3967fcb87d113287ec))
* **commitlint:** fix local running of commit linter on macOS ([#249](https://github.com/tiborsimko/reana-db/issues/249)) ([b13bb3b](https://github.com/tiborsimko/reana-db/commit/b13bb3bae824ee2eb39aa8328bbda111c1b80f75))
* **commitlint:** improve checking of merge commits ([#236](https://github.com/tiborsimko/reana-db/issues/236)) ([67a7254](https://github.com/tiborsimko/reana-db/commit/67a72544e4e0abcfacdc6cd81e1267de959d82e7))
* pin ubuntu version in GA jobs ([712b138](https://github.com/tiborsimko/reana-db/commit/712b13893c72420a596f42b9a9496c7e93ff4624))
* **pytest:** invoke `pytest` directly instead of `setup.py test` ([#237](https://github.com/tiborsimko/reana-db/issues/237)) ([6b23c4d](https://github.com/tiborsimko/reana-db/commit/6b23c4de09aea1758b2cffa62fbdd8a09ba0a150))
* **pytest:** move to PostgreSQL 14.10 ([#226](https://github.com/tiborsimko/reana-db/issues/226)) ([4dac889](https://github.com/tiborsimko/reana-db/commit/4dac88953754c0810d3502e8e511ec90c27c2b43))
* **python:** pin setuptools below 81 ([#253](https://github.com/tiborsimko/reana-db/issues/253)) ([8b25e00](https://github.com/tiborsimko/reana-db/commit/8b25e0092e7709da889db04bb1907c4e2322601a))
* **python:** test more Python versions ([#239](https://github.com/tiborsimko/reana-db/issues/239)) ([e0cba7f](https://github.com/tiborsimko/reana-db/commit/e0cba7faa97cbf2919c4008ec884ea46ec817cd5))
* **release-please:** initial configuration ([#218](https://github.com/tiborsimko/reana-db/issues/218)) ([7c616d6](https://github.com/tiborsimko/reana-db/commit/7c616d67fac642656f56d37422ba69c4a8d4fa20))
* **runners:** upgrade CI runners to Ubuntu 22.04 ([#243](https://github.com/tiborsimko/reana-db/issues/243)) ([020c324](https://github.com/tiborsimko/reana-db/commit/020c324f2e631a34295492493bedb424c5e372a3))
* **runners:** upgrade CI runners to Ubuntu 22.04 ([#243](https://github.com/tiborsimko/reana-db/issues/243)) ([1d929ba](https://github.com/tiborsimko/reana-db/commit/1d929ba779e66bd531b348ae60fac506a79ec96f))
* **shellcheck:** fix exit code propagation ([#223](https://github.com/tiborsimko/reana-db/issues/223)) ([b62ee1e](https://github.com/tiborsimko/reana-db/commit/b62ee1e3be44628265bf5ada7e0b7eb88e283c00))
* update all actions ([50b73e2](https://github.com/tiborsimko/reana-db/commit/50b73e238eec5d9a6204b90c22b7d554208f53d6))


### Documentation

* add .readthedocs.yaml to migrate to RTD v2 ([6524827](https://github.com/tiborsimko/reana-db/commit/6524827d45b46427941b1065050be4dc5544ac0d))
* **authors:** complete list of contributors ([#227](https://github.com/tiborsimko/reana-db/issues/227)) ([3fbcf65](https://github.com/tiborsimko/reana-db/commit/3fbcf65db735146d54078cae4c5b9c8968ead055))
* fix rtfd build badge so it shows the real status ([51f36b9](https://github.com/tiborsimko/reana-db/commit/51f36b91bbf67f3e494081b530c28bd0e2b0dc4f))
* include modules documentation ([fd5c7b1](https://github.com/tiborsimko/reana-db/commit/fd5c7b160ab083c535276d1af7de7fd554d8e8b2))
* Python versions shield ([ec55933](https://github.com/tiborsimko/reana-db/commit/ec559332f636b1bf8c7a735de79acb493b88a52b))
* replace reference to analyse with workflow ([73b9339](https://github.com/tiborsimko/reana-db/commit/73b93392d92418d101fe2b3eefbe94929173be8f))
* set default language to English ([7a21184](https://github.com/tiborsimko/reana-db/commit/7a211845c893fe418d2a47efb3e18ed16c22b006))
* single-page RTFD outline ([ce07a07](https://github.com/tiborsimko/reana-db/commit/ce07a07ec6f5bb667fb20ee66aca48fa68f61836))
* use REANA logo ([6d632e0](https://github.com/tiborsimko/reana-db/commit/6d632e073fca55243677aa10bd8675d43e50fd28))


### Chores

* **master:** release 0.95.0a1 ([ec7c5e5](https://github.com/tiborsimko/reana-db/commit/ec7c5e5801fb7954bc8b8e652674e64d67526838))

## [0.9.5](https://github.com/reanahub/reana-db/compare/0.9.4...0.9.5) (2024-11-26)


### Features

* **cli:** add new `migrate-secret-key` command ([#240](https://github.com/reanahub/reana-db/issues/240)) ([efcbe72](https://github.com/reanahub/reana-db/commit/efcbe724a2797edf94a531a2fd49ae0dc25d29f7))


### Continuous integration

* **actions:** pin setuptools 70 ([#239](https://github.com/reanahub/reana-db/issues/239)) ([3202759](https://github.com/reanahub/reana-db/commit/320275969c64513f695ce59a145088f6222aa594))
* **python:** test more Python versions ([#239](https://github.com/reanahub/reana-db/issues/239)) ([e0cba7f](https://github.com/reanahub/reana-db/commit/e0cba7faa97cbf2919c4008ec884ea46ec817cd5))

## [0.9.4](https://github.com/reanahub/reana-db/compare/0.9.3...0.9.4) (2024-03-01)


### Code refactoring

* **docs:** move from reST to Markdown ([#225](https://github.com/reanahub/reana-db/issues/225)) ([b48eb55](https://github.com/reanahub/reana-db/commit/b48eb55f7a1b1bbdde0e0a458852349a439a511e))


### Code style

* **black:** format with black v24 ([#224](https://github.com/reanahub/reana-db/issues/224)) ([cc60522](https://github.com/reanahub/reana-db/commit/cc6052242fd14cf3413b793d0aa32a24871fe1b1))


### Continuous integration

* **commitlint:** addition of commit message linter ([#218](https://github.com/reanahub/reana-db/issues/218)) ([ee0f7e5](https://github.com/reanahub/reana-db/commit/ee0f7e5e106e0be619779bfa2133415feecc323b))
* **commitlint:** allow release commit style ([#229](https://github.com/reanahub/reana-db/issues/229)) ([adf15d7](https://github.com/reanahub/reana-db/commit/adf15d7c6457eddadc3da1aa8b95b74cfc1239fb))
* **commitlint:** check for the presence of concrete PR number ([#223](https://github.com/reanahub/reana-db/issues/223)) ([3d513f6](https://github.com/reanahub/reana-db/commit/3d513f6cda44e9e40b3c8f3967fcb87d113287ec))
* **pytest:** move to PostgreSQL 14.10 ([#226](https://github.com/reanahub/reana-db/issues/226)) ([4dac889](https://github.com/reanahub/reana-db/commit/4dac88953754c0810d3502e8e511ec90c27c2b43))
* **release-please:** initial configuration ([#218](https://github.com/reanahub/reana-db/issues/218)) ([7c616d6](https://github.com/reanahub/reana-db/commit/7c616d67fac642656f56d37422ba69c4a8d4fa20))
* **shellcheck:** fix exit code propagation ([#223](https://github.com/reanahub/reana-db/issues/223)) ([b62ee1e](https://github.com/reanahub/reana-db/commit/b62ee1e3be44628265bf5ada7e0b7eb88e283c00))


### Documentation

* **authors:** complete list of contributors ([#227](https://github.com/reanahub/reana-db/issues/227)) ([3fbcf65](https://github.com/reanahub/reana-db/commit/3fbcf65db735146d54078cae4c5b9c8968ead055))

## 0.9.3 (2023-12-01)

- Changes the `Workflow` table to replace the `run_number` column with two new columns `run_number_major` and `run_number_minor` in order to allow for more than nine restarts of user workflows.
- Changes the names of database table, column, index and key constraints in order to follow the SQLAlchemy upstream naming conventions everywhere.
- Changes several database index definitions in order to improve performance of most common database queries.

## 0.9.2 (2023-09-26)

- Adds progress meter to the logs of the periodic quota updater.
- Changes CPU and disk quota calculations to improve the performance of periodic quota updater.
- Fixes the workflow priority calculation to avoid workflows stuck in the `queued` status when the number of allowed concurrent workflow is set to zero.

## 0.9.1 (2023-01-18)

- Changes to PostgreSQL 12.13.
- Fixes conversion of possibly-negative resource usage values to human-readable formats.
- Fixes disk quota updater to prevent setting negative disk quota usage values.
- Fixes quota updater to reduce memory usage.

## 0.9.0 (2022-12-13)

- Adds new `launcher_url` column to the `Workflow` table to store the remote origin of workflows submitted via the Launch-on-REANA functionality.
- Adds the possibility to force resource quota updates irrespective of globally-configured quota update policy.
- Adds new `WorkspaceRetentionRule` table to store workspace file retention rules.
- Adds new `WorkspaceRetentionAuditLog` table to store the audit log of workspace file retention rule updates.
- Changes percentage ranges used to calculate the health status of user resource quota usage.
- Changes to PostgreSQL 12.10.
- Fixes wrong numbering of restarted workflows by limiting the number of times a workflow can be restarted to nine.
- Fixes `Workflow.get_workspace_disk_usage` to always calculate disk usage rather than relying on the quota usage values from the database, since these may not be up-to-date depending on the global quota update policy.
- Fixes helper function that retrieves workflows by UUID to also additionally check that the provided user is the owner of the workflow.

## 0.8.2 (2022-02-23)

- Adds transition for workflow from queued to failed status.

## 0.8.1 (2022-02-01)

- Adds an option to periodically calculate CPU quota usage.
- Changes CLI quota command from `disk-usage-update` to `resource-usage-update` since it can also perform CPU quota calculation.
- Fixes quota update functions to handle exceptional situation as continuable errors.
- Removes extra `QuotaResourceType` enum in favor of `ResourceType.name`.

## 0.8.0 (2021-11-22)

- Adds new disk usage retrieval methods using canonical (bytes) and human-readable (KiB) units. (`User`, `Workflow`)
- Adds Quota models which calculates CPU and disk usage.
- Adds `InteractiveSession` model.
- Adds new properties `started_at` and `finished_at` to the `Job` model, updated on status change.
- Adds `get_priority` workflow method, that combines both complexity and concurrency, to pass to the scheduler.
- Adds a possibility to configure database connection pool parameters via environment variables.
- Adds new `pending` state to `RunStatus` table.
- Adds workflow complexity property in `Workflow` table.
- Adds environment variable to configure which quotas to update.
- Changes `WorkflowStatus` table to `RunStatus`.
- Changes disk quota calculation functions to allow passing raw bytes to increase the used quota.
- Changes to PostgreSQL 12.8.
- Removes support for Python 2.

## 0.7.3 (2021-03-17)

- Fixes REANA installation by pinning SQLAlchemy version less than 1.4.0 due to <https://github.com/kvesteri/sqlalchemy-utils/issues/505>.

## 0.7.2 (2021-02-22)

- Adds utility to status enums to decide whether to clean workflows and jobs depending on their status.

## 0.7.1 (2021-02-02)

- Adds support for Python 3.9.
- Fixes minor code warnings.
- Changes CI system to include Python flake8 checker.

## 0.7.0 (2020-10-20)

- Adds initial central workflow status transition logic handler.
- Adds new audit table and logic to register actions. (`AuditLog`, `AuditLogAction`)
- Adds fixtures for better testing of database models.
- Changes user token storage to move tokens from `User` table to `UserToken` table and to encrypt them.
- Changes `Workflow` table to add a new `workspace_path` column.
- Changes default database service to use centrally configured one from REANA-Commons. (`REANA_INFRASTRUCTURE_COMPONENTS_HOSTNAMES`)
- Changes code formatting to respect `black` coding style.
- Changes documentation to single-page layout.

## 0.6.0 (2019-12-19)

- Adds new method which returns full workflow name.
- Adds more granular DB configuration.
- Adds Git repository information to the workflow model.
  (`Workflow.git_repo`, `Workflow.git_provider`)
- Adds user name information to the user model.
  (`User.full_name`, `User.username`)
- Removes restart count information from the job model.
  (`Job.restart_count`, `Job.max_restart_count`)
- Adds support for Python 3.8.

## 0.5.0 (2019-04-16)

- Introduces new workflow statuses: `deleted`, `stopped`, `queued`.
- Adds new field to store workflow stopping time. (`Workflow.run_stopped_at`)
- Moves workflow input parameters to its own column to separate them from
  operational options. Adapts getters accordingly.
  (`Workflow.input_parameters`)
- Adds new method to retrieve the workflow owner's token.
  (`Workflow.get_owner_access_token`)
- Introduces new utility function to retrieve workflows by `uuid` or name.
  (`_get_workflow_with_uuid_or_name`)
- Introduces new fields for interactive sessions: `interactive_session`,
  `interactive_session_name` and `interactive_session_type`. Note that with
  current design only one interactive session per workflow is supported.
- Adds a new enumeration for possible job statuses. (`JobStatus`)
- Adds new field to identify jobs in the underlying compute backend.
  (`Job.backend_job_id`)

## 0.4.0 (2018-11-06)

- Stores `reana.yaml` in database models.
- Adds Workflow specification and parameter getters.
- Adds support for Python 3.7.
- Changes license to MIT.

## 0.3.0 (2018-08-10)

- This package is a result of refactoring [reana-commons](https://reana-commons.readthedocs.io/).
- Provides common REANA models.
- Provides database connection logic.
