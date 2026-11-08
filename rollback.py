"""Undoes migrate.py: deletes every exported claim from the target table. Safe to run after a
partial copy, twice, or when the table is already gone."""

import boto3
from botocore.exceptions import ClientError

from claims_export import read_rows, table_name


def main():
    table = boto3.resource("dynamodb").Table(table_name())
    rows = read_rows()
    try:
        with table.batch_writer() as batch:
            for row in rows:
                batch.delete_item(Key={"claim_id": row["CLAIM_ID"]})
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"{table.name} doesn't exist; nothing to undo")
            return
        raise
    print(f"removed {len(rows)} claims from {table.name}")


if __name__ == "__main__":
    main()
