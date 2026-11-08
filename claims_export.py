"""Reads the CLAIMS_DB export taken from the on-prem Oracle database and maps rows to the
target DynamoDB items. Shared by migrate.py, verify.py and rollback.py."""

import csv
import os
from decimal import Decimal
from pathlib import Path

EXPORT = Path(__file__).resolve().parent / "data" / "claims_export.csv"


def table_name(env: str | None = None) -> str:
    """mac-claims-<env>-claims, created by claims-service-iac (terraform/storage)."""
    env = env or os.environ.get("MAC_ENV")
    if env not in ("rehearsal", "production"):
        raise SystemExit(f"MAC_ENV must be rehearsal or production, got {env!r}")
    return f"mac-claims-{env}-claims"


def read_rows(path: Path = EXPORT) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_item(row: dict) -> dict:
    """One export row -> one DynamoDB item, with the target schema's field names."""
    return {
        "claim_id": row["CLAIM_ID"],
        "member_id": row["MEMBER_ID"],
        "provider_id": row["PROVIDER_ID"],
        "service_date": row["SERVICE_DATE"],
        "amount": Decimal(row["AMOUNT"]),
        "diagnosis_code": row["DIAGNOSIS_CODE"],
        "status": row["CLAIM_STATUS"].lower(),
    }
