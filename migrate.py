"""Loads the CLAIMS_DB export into the target claims table. Safe to re-run: writing the same
claim twice overwrites it."""

import boto3

from claims_export import read_rows, table_name, to_item


def main():
    table = boto3.resource("dynamodb").Table(table_name())
    rows = read_rows()
    print(f"loading {len(rows)} claims into {table.name}")
    with table.batch_writer() as batch:
        for row in rows:
            batch.put_item(Item=to_item(row))
    print(f"loaded {len(rows)} claims")


if __name__ == "__main__":
    main()
