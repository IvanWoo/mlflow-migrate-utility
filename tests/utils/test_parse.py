import pytest

from mlflow_migrate_utility.utils import ArtifactLocation, parse


def test_parse():
    with pytest.raises(ValueError, match="Invalid CloudVendor name"):
        parse(
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "42",
        )


def test_parse_aws():
    assert parse("s3://mlflow.artifacts/prediction/1", "aws") == ArtifactLocation(
        "s3", "mlflow.artifacts", "prediction/1"
    )
    assert parse("s3://mlflow-artifacts/prediction/1", "aws") == ArtifactLocation(
        "s3", "mlflow-artifacts", "prediction/1"
    )
    assert parse("s3://dummy/prediction", "aws") == ArtifactLocation(
        "s3", "dummy", "prediction"
    )


def test_parse_azure():
    assert (
        parse(
            "wasbs://mlflow-artifacts@storageaccount.blob.core.windows.net/prediction/1",
            "azure",
        )
        == ArtifactLocation(
            "wasbs", "mlflow-artifacts", "prediction/1", "storageaccount"
        )
    )
    assert parse(
        "wasbs://dummy@storageaccount.blob.core.windows.net/prediction/1/2/3", "azure"
    ) == ArtifactLocation("wasbs", "dummy", "prediction/1/2/3", "storageaccount")
