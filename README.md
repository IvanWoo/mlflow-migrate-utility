# mlflow-migrate-utility

## Requirements

- [pyenv](https://github.com/pyenv/pyenv)
- [pipenv](https://github.com/pypa/pipenv)

Tested with
- MLflow 1.11.0
- Python 3.8.6

## Setup

```sh
$ pipenv install --dev
$ pipenv shell
```

## Usage

```
$ mmu --help
Usage: mmu [OPTIONS]

  mlflow-migrate-utility: mmu
  Utility for updating the MLflow metadata after migrating artifacts backend from different cloud vendors.

Options:
  --origin [aws|azure]    [required]
  --target [aws|azure]    [required]
  --storage-account TEXT  Storage account of Azure  [default: ]
  --database-url TEXT     Only support Postgresql for now  [required]
  --version               Show the version and exit.
  --help                  Show this message and exit.
```

## Examples

### Migrate from S3 to Azure blob

after copying artifacts from AWS S3 to Azure blob and restoring the database, we need to update the metadata to picking the new cloud storage

```
$ mmu --origin aws --target azure --database-url "postgresql://username:password@localhost:5432/mlflow" --storage-account azureStorageAccount
```

### Move to a new Azure storage account

```
$ mmu --origin azure --target azure --database-url "postgresql://username:password@localhost:5432/mlflow" --storage-account newAzureStorageAccount
```

## Development

```sh
$ pipenv install --dev
$ pipenv shell
$ pre-commit install
```

## Testing

```sh
$ pipenv run test
```

## TODO

- end to end test
- support other database backend besides `PostgreSQL`
- support other cloud vendor besides `AWS` and `Azure`
