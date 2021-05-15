import pytest

from mlflow_migrate_utility.exceptions import InvalidLocationError
from mlflow_migrate_utility.utils import convert


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
