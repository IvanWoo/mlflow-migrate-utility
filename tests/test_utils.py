import pytest

from mlflow_migrate_utility.exceptions import InvalidLocationError
from mlflow_migrate_utility.utils import (
    ArtifactLocation,
    concat,
    concat_aws,
    concat_azure,
    convert,
    parse,
    parse_aws,
    parse_azure,
)


def test_parse():
    with pytest.raises(ValueError, match="Invalid CloudVendor name"):
        parse(
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "42",
        )


def test_parse_aws():
    assert parse_aws("s3://mlflow.artifacts/prediction/1") == ArtifactLocation(
        "s3", "mlflow.artifacts", "prediction/1"
    )
    assert parse_aws("s3://mlflow-artifacts/prediction/1") == ArtifactLocation(
        "s3", "mlflow-artifacts", "prediction/1"
    )
    assert parse_aws("s3://dummy/prediction") == ArtifactLocation(
        "s3", "dummy", "prediction"
    )


def test_parse_azure():
    assert parse_azure(
        "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1"
    ) == ArtifactLocation("wasbs", "mlflow-artifacts", "prediction/1", "storageaccount")
    assert parse_azure(
        "wasbs://dummy@storageaccount.blob.core.windows.net/prediction/1/2/3"
    ) == ArtifactLocation("wasbs", "dummy", "prediction/1/2/3", "storageaccount")


def test_concat():
    with pytest.raises(ValueError, match="Invalid CloudVendor name"):
        concat(
            ArtifactLocation(
                "wasbs", "mlflow-artifacts", "prediction/1", "storageaccount"
            ),
            "42",
        )


def test_concat_aws():
    assert (
        concat_aws(ArtifactLocation("s3", "mlflow.artifacts", "prediction/1"))
        == "s3://mlflow.artifacts/prediction/1"
    )
    assert (
        concat_aws(ArtifactLocation("s3", "mlflow-artifacts", "prediction/1"))
        == "s3://mlflow-artifacts/prediction/1"
    )
    assert (
        concat_aws(ArtifactLocation("s3", "dummy", "prediction"))
        == "s3://dummy/prediction"
    )


def test_concat_azure():
    assert (
        concat_azure(
            ArtifactLocation(
                "wasbs", "mlflow-artifacts", "prediction/1", "storageaccount"
            )
        )
        == "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1"
    )
    assert (
        concat_azure(
            ArtifactLocation("wasbs", "dummy", "prediction/1/2/3", "storageaccount")
        )
        == "wasbs://dummy@storageaccount.blob.core.windows.net/prediction/1/2/3"
    )


def test_convert():
    # azure -> aws
    assert (
        convert(
            "wasbs://dummy@storageaccount.blob.core.windows.net/prediction/1/2/3",
            "azure",
            "aws",
            "placeholder",
        )
        == "s3://dummy/prediction/1/2/3"
    )
    assert (
        convert(
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            "aws",
            "placeholder",
        )
        == "s3://mlflow-artifacts/prediction/1"
    )

    # aws -> azure
    assert (
        convert(
            "s3://mlflow-artifacts/prediction/1",
            "aws",
            "azure",
            "dummy",
        )
        == "wasbs://mlflow-artifacts@dummy.blob.core.windows.net/prediction/1"
    )
    assert (
        convert(
            "s3://mlflow.artifacts/prediction/1",
            "aws",
            "azure",
            "dummy",
        )
        == "wasbs://mlflow-artifacts@dummy.blob.core.windows.net/prediction/1"
    )

    # azure -> azure with changing storage account
    assert (
        convert(
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            "azure",
            "placeholder",
        )
        == "wasbs://mlflow-artifacts@placeholder.blob.core.windows.net/prediction/1"
    )
    assert (
        convert(
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            "azure",
            "dummy",
        )
        == "wasbs://mlflow-artifacts@dummy.blob.core.windows.net/prediction/1"
    )


def test_convert_invalid_location():
    with pytest.raises(InvalidLocationError):
        convert("invalid-location", "", "", "")


def test_convert_empty_storage_account():
    assert (
        convert(
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            "aws",
            "",
        )
        == "s3://mlflow-artifacts/prediction/1"
    )

    with pytest.raises(
        ValueError, match="Storage account cannot be empty for Azure target"
    ):
        convert(
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            "azure",
            "",
        )
