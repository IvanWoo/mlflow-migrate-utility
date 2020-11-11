from functools import partial

import click

from mlflow_migrate_utility.utils import update_artifact_location

click.option = partial(click.option, show_default=True)


@click.command()
@click.option(
    "--origin", required=True, type=click.Choice(["aws", "azure"], case_sensitive=False)
)
@click.option(
    "--target", required=True, type=click.Choice(["aws", "azure"], case_sensitive=False)
)
@click.option("--storage-account", default="", help="Storage account of Azure")
@click.option("--database-url", required=True, help="Only support Postgresql for now")
@click.version_option()
def main(origin, target, storage_account, database_url):
    """
    \b
    mlflow-migrate-utility: mmu
    Utility for updating the MLflow metadata after migrating artifacts backend from different cloud vendors.
    """
    update_artifact_location(origin, target, storage_account, database_url)
