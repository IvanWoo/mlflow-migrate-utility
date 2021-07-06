import pytest

from mlflow_migrate_utility.exceptions import (
    EmptyStorageAccountError,
    InvalidLocationError,
)
from mlflow_migrate_utility.utils import convert


@pytest.mark.parametrize(
    "location, origin, target, storage_account, expected",
    [
        # azure -> aws
        (
            "wasbs://dummy@storageaccount.blob.core.windows.net/prediction/1/2/3",
            "azure",
            "aws",
            "placeholder",
            "s3://dummy/prediction/1/2/3",
        ),
        (
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            "aws",
            "placeholder",
            "s3://mlflow-artifacts/prediction/1",
        ),
        (
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            "aws",
            "",
            "s3://mlflow-artifacts/prediction/1",
        ),
        # aws -> azure
        (
            "s3://mlflow-artifacts/prediction/1",
            "aws",
            "azure",
            "dummy",
            "wasbs://mlflow-artifacts@dummy.blob.core.windows.net/prediction/1",
        ),
        (
            "s3://mlflow.artifacts/prediction/1",
            "aws",
            "azure",
            "dummy",
            "wasbs://mlflow-artifacts@dummy.blob.core.windows.net/prediction/1",
        ),
        # azure -> azure with changing storage account
        (
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            "azure",
            "placeholder",
            "wasbs://mlflow-artifacts@placeholder.blob.core.windows.net/prediction/1",
        ),
        (
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            "azure",
            "dummy",
            "wasbs://mlflow-artifacts@dummy.blob.core.windows.net/prediction/1",
        ),
    ],
)
def test_convert__success(
    location: str, origin: str, target: str, storage_account: str, expected: str
):
    assert convert(location, origin, target, storage_account) == expected


@pytest.mark.parametrize(
    "location, origin, target, storage_account, expected_error",
    [
        ("invalid-location", "", "", "", InvalidLocationError),
        (
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            "azure",
            "",
            EmptyStorageAccountError,
        ),
    ],
)
def test_convert__error(
    location: str, origin: str, target: str, storage_account: str, expected_error
):
    with pytest.raises(expected_error):
        convert(location, origin, target, storage_account)
