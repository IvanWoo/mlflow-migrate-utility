import pytest

from mlflow_migrate_utility.exceptions import InvalidCloudVendorError
from mlflow_migrate_utility.utils import ArtifactLocation, parse


@pytest.mark.parametrize(
    "location, vendor, expected_error",
    [
        (
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "42",
            InvalidCloudVendorError,
        ),
    ],
)
def test_parse__error(location, vendor, expected_error):
    with pytest.raises(expected_error):
        parse(location, vendor)


@pytest.mark.parametrize(
    "location, vendor, expected",
    [
        (
            "s3://mlflow.artifacts/prediction/1",
            "aws",
            ArtifactLocation("s3", "mlflow.artifacts", "prediction/1"),
        ),
        (
            "s3://mlflow-artifacts/prediction/1",
            "aws",
            ArtifactLocation("s3", "mlflow-artifacts", "prediction/1"),
        ),
        (
            "s3://dummy/prediction",
            "aws",
            ArtifactLocation("s3", "dummy", "prediction"),
        ),
        (
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
            ArtifactLocation(
                "wasbs", "mlflow-artifacts", "prediction/1", "storageaccount"
            ),
        ),
        (
            "wasbs://dummy@storageaccount.blob.core.windows.net/prediction/1/2/3",
            "azure",
            ArtifactLocation("wasbs", "dummy", "prediction/1/2/3", "storageaccount"),
        ),
    ],
)
def test_parse__success(location, vendor, expected):
    assert parse(location, vendor) == expected
