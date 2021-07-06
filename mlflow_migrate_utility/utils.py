from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras

from mlflow_migrate_utility.exceptions import (
    EmptyStorageAccountError,
    InvalidCloudVendorError,
    InvalidLocationError,
)
from mlflow_migrate_utility.log import get_logger

logger = get_logger(__name__)


class CloudVendor(str, Enum):
    AWS = "aws"
    AZURE = "azure"


@dataclass
class ArtifactLocation:
    schema: str
    bucket_name: str
    prefix: str
    # azure blob specific
    storage_account: str = ""


def parse_aws(location: str) -> ArtifactLocation:
    """Parse artifact location of aws s3"""
    p = urlparse(location)
    schema, name, prefix = p.scheme, p.netloc, p.path.lstrip("/")
    return ArtifactLocation(schema, name, prefix)


def parse_azure(location: str) -> ArtifactLocation:
    """Parse artifact location of azure blob"""
    p = urlparse(location)
    schema, name_storage_account, prefix = p.scheme, p.netloc, p.path.lstrip("/")
    name, storage_account = name_storage_account.split("@")
    storage_account = storage_account.split(".")[0]
    return ArtifactLocation(schema, name, prefix, storage_account)


def parse(location: str, vendor: str) -> ArtifactLocation:
    """Parse artifact location"""
    if vendor == CloudVendor.AWS:
        return parse_aws(location)
    elif vendor == CloudVendor.AZURE:
        return parse_azure(location)
    else:
        raise InvalidCloudVendorError


def concat_aws(location: ArtifactLocation) -> str:
    return f"{location.schema}://{location.bucket_name}/{location.prefix}"


def concat_azure(location: ArtifactLocation) -> str:
    return f"{location.schema}://{location.bucket_name}@{location.storage_account}.blob.core.windows.net/{location.prefix}"


def concat(location: ArtifactLocation, vendor: str) -> str:
    if vendor == CloudVendor.AWS:
        return concat_aws(location)
    elif vendor == CloudVendor.AZURE:
        return concat_azure(location)
    else:
        raise InvalidCloudVendorError


def is_valid(location: str):
    for schema in ["s3", "wasbs"]:
        if location.startswith(schema):
            return True
    return False


def get_schema(vendor: str) -> str:
    mapping = {CloudVendor.AWS: "s3", CloudVendor.AZURE: "wasbs"}
    return mapping[vendor]


def convert(location: str, origin: str, target: str, storage_account: str) -> str:
    if not is_valid(location):
        raise InvalidLocationError(f"Invalid location: {location}")
    if target == CloudVendor.AZURE and not storage_account:
        raise EmptyStorageAccountError(
            "Storage account cannot be empty for Azure target"
        )

    al = parse(location, origin)
    al.schema = get_schema(target)
    if target == CloudVendor.AZURE:
        # TODO: make this behavior configurable
        # dot(.) is invalid as azure blob bucket name
        al.bucket_name = "-".join(al.bucket_name.split("."))
    al.storage_account = storage_account
    return concat(al, target)


def update_table(
    cur,
    origin: str,
    target: str,
    storage_account: str,
    table: str,
    id_col: str,
    location_col: str,
) -> None:
    """Update the table that has the artifacts location column

    Args:
        cur ([type]): [description]
        origin (str): [description]
        target (str): [description]
        storage_account (str): [description]
        table (str): table name
        id_col (str): colum name of unique id that distingushes each row
        location_col (str): colum name of location
    """
    cur.execute(f"SELECT {id_col}, {location_col} FROM {table}")

    new_rs = dict()
    for r in cur.fetchall():
        try:
            new_rs[r[0]] = convert(r[1], origin, target, storage_account)
        except InvalidLocationError as e:
            logger.warning(e)
    query = f"UPDATE {table} SET {location_col} = (%s) WHERE {id_col} = (%s)"
    vals = [(v, k) for k, v in new_rs.items()]
    psycopg2.extras.execute_batch(cur, query, vals)
    return


def update_artifact_location(origin, target, storage_account, database_url) -> None:
    with psycopg2.connect(database_url, sslmode="prefer") as conn:
        with conn.cursor() as cur:
            for table, id_col, location_col in [
                ("experiments", "experiment_id", "artifact_location"),
                ("model_versions", "run_id", "source"),
                ("runs", "run_uuid", "artifact_uri"),
            ]:
                logger.info(f"Update {table=}")
                update_table(
                    cur, origin, target, storage_account, table, id_col, location_col
                )

        logger.info("Commit")
        conn.commit()
