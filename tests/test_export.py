import sys
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from claims_export import oracle_date_to_iso, read_rows, table_name, to_item  # noqa: E402


def test_export_has_every_claim_once():
    ids = [row["CLAIM_ID"] for row in read_rows()]
    assert len(ids) == 12 and len(set(ids)) == 12


def test_rows_map_to_the_target_schema():
    item = to_item(read_rows()[0])
    assert item["claim_id"] == "CLM-1001" and item["member_id"] == "M-20001"
    assert item["amount"] == Decimal("120.50") and item["status"] == "submitted"
    assert set(item) == {"claim_id", "member_id", "provider_id", "service_date", "amount",
                         "diagnosis_code", "status"}


def test_amounts_keep_their_cents():
    assert sum(to_item(r)["amount"] for r in read_rows()) == Decimal("14047.84")


def test_table_name_per_environment(monkeypatch):
    assert table_name("rehearsal") == "mac-claims-rehearsal-claims"
    monkeypatch.setenv("MAC_ENV", "production")
    assert table_name() == "mac-claims-production-claims"
    with pytest.raises(SystemExit):
        table_name("staging")


def test_service_dates_are_iso_8601():
    assert oracle_date_to_iso("01-JAN-24") == "2024-01-01"
    assert oracle_date_to_iso("2024-03-22") == "2024-03-22"
    assert to_item(read_rows()[0])["service_date"] == "2024-01-01"
    for row in read_rows():
        assert len(to_item(row)["service_date"]) == 10 and to_item(row)["service_date"][4] == "-"
    with pytest.raises(ValueError):
        oracle_date_to_iso("31/12/2024")
