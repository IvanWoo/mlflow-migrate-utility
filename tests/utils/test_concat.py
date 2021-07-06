import pytest

from mlflow_migrate_utility.exceptions import InvalidCloudVendorError
from mlflow_migrate_utility.utils import ArtifactLocation, concat


@pytest.mark.parametrize(
    "location, vendor, expected_error",
    [
        (
            ArtifactLocation(
                "wasbs", "mlflow-artifacts", "prediction/1", "storageaccount"
            ),
            "42",
            InvalidCloudVendorError,
        ),
    ],
)
def test_concat__error(location, vendor, expected_error):
    with pytest.raises(expected_error):
        concat(location, vendor)


@pytest.mark.parametrize(
    "location, vendor, expected",
    [
        (
            ArtifactLocation("s3", "mlflow.artifacts", "prediction/1"),
            "aws",
            "s3://mlflow.artifacts/prediction/1",
        ),
        (
            ArtifactLocation("s3", "mlflow-artifacts", "prediction/1"),
            "aws",
            "s3://mlflow-artifacts/prediction/1",
        ),
        (
            ArtifactLocation("s3", "dummy", "prediction"),
            "aws",
            "s3://dummy/prediction",
        ),
        (
            ArtifactLocation(
                "wasbs", "mlflow-artifacts", "prediction/1", "storageaccount"
            ),
            "azure",
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
        ),
        (
            ArtifactLocation("wasbs", "dummy", "prediction/1/2/3", "storageaccount"),
            "azure",
            "wasbs://dummy@storageaccount.blob.core.windows.net/prediction/1/2/3",
        ),
    ],
)
def test_concat__success(location, vendor, expected):
    assert concat(location, vendor) == expected
