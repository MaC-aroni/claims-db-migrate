"""Checks the copy: every exported claim is in the target table, and nothing else is."""

import sys

import boto3

from claims_export import read_rows, table_name


def count_items(table) -> int:
    total, kwargs = 0, {"Select": "COUNT"}
    while True:
        page = table.scan(**kwargs)
        total += page["Count"]
        if "LastEvaluatedKey" not in page:
            return total
        kwargs["ExclusiveStartKey"] = page["LastEvaluatedKey"]


def main():
    table = boto3.resource("dynamodb").Table(table_name())
    expected = [row["CLAIM_ID"] for row in read_rows()]
    found = count_items(table)
    print(f"export: {len(expected)} claims, {table.name}: {found} items")
    missing = [cid for cid in expected if "Item" not in table.get_item(Key={"claim_id": cid}, ProjectionExpression="claim_id")]
    if missing:
        sys.exit(f"missing from {table.name}: {', '.join(missing)}")
    if found != len(expected):
        sys.exit(f"row counts differ: export has {len(expected)}, table has {found}")
    print("verified: every claim copied, counts match")


if __name__ == "__main__":
    main()
