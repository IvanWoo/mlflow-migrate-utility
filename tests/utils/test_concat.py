import pytest

from mlflow_migrate_utility.utils import ArtifactLocation, concat


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
        concat(ArtifactLocation("s3", "mlflow.artifacts", "prediction/1"), "aws")
        == "s3://mlflow.artifacts/prediction/1"
    )
    assert (
        concat(ArtifactLocation("s3", "mlflow-artifacts", "prediction/1"), "aws")
        == "s3://mlflow-artifacts/prediction/1"
    )
    assert (
        concat(ArtifactLocation("s3", "dummy", "prediction"), "aws")
        == "s3://dummy/prediction"
    )


def test_concat_azure():
    assert (
        concat(
            ArtifactLocation(
                "wasbs", "mlflow-artifacts", "prediction/1", "storageaccount"
            ),
            "azure",
        )
        == "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1"
    )
    assert (
        concat(
            ArtifactLocation("wasbs", "dummy", "prediction/1/2/3", "storageaccount"),
            "azure",
        )
        == "wasbs://dummy@storageaccount.blob.core.windows.net/prediction/1/2/3"
    )
