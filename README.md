# claims-db-migrate

Moves CLAIMS_DB from the on-prem Oracle database to the claims table in AWS. Owned by the
DBA team.

| File | Used by MaC step | What it does |
|---|---|---|
| `migrate.py` | `db_migrate` (run) | Loads `data/claims_export.csv` (the Oracle export) into `mac-claims-<env>-claims` |
| `verify.py` | `db_migrate` (verify) | Every exported claim is in the table, and the counts match |
| `rollback.py` | `db_migrate` (undo) | Deletes the migrated claims; safe to re-run |

## Naming contract (shared by all four repos)

MaC passes `MAC_ENV` (`rehearsal` or `production`) to every step, and every resource name
includes it, so a rehearsal never touches production:

| Resource | Name |
|---|---|
| Claims table (DynamoDB) | `mac-claims-<env>-claims` |
| Service role / Lambda | `mac-claims-<env>-service` |
| MCP tool role / Lambda | `mac-claims-<env>-mcp` |

Every AWS resource is tagged `mac:env`, `mac:migration` and `mac:deployment-id` (the MaC run
that last changed it), so you can see in the AWS console which deployment made what.

## How it runs

MaC checks this repo's `main` out at the exact commit Build locked and runs it; see
[MaC's runner docs](https://github.com/MaC-aroni/deployed-on-a-prayer/blob/main/docs/runner.md).
Build only runs code whose CI passed and that reached `main` through an approved pull request,
so **every change here goes through a reviewed PR**.

Local checks: `pip install -r requirements-dev.txt && python -m pytest`
