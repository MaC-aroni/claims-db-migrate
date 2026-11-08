"""Reads the CLAIMS_DB export taken from the on-prem Oracle database and maps rows to the
target DynamoDB items. Shared by migrate.py, verify.py and rollback.py."""

import csv
import os
from datetime import datetime
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


def oracle_date_to_iso(value: str) -> str:
    """Oracle's default DATE export (DD-MON-YY, e.g. 01-JAN-24) -> ISO 8601 (2024-01-01), the
    format the target schema and the claims service read. ISO dates pass through unchanged."""
    value = value.strip()
    for fmt in ("%d-%b-%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.title() if fmt == "%d-%b-%y" else value, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"unrecognised service date {value!r}")


def to_item(row: dict) -> dict:
    """One export row -> one DynamoDB item, with the target schema's field names."""
    return {
        "claim_id": row["CLAIM_ID"],
        "member_id": row["MEMBER_ID"],
        "provider_id": row["PROVIDER_ID"],
        "service_date": oracle_date_to_iso(row["SERVICE_DATE"]),
        "amount": Decimal(row["AMOUNT"]),
        "diagnosis_code": row["DIAGNOSIS_CODE"],
        "status": row["CLAIM_STATUS"].lower(),
    }
