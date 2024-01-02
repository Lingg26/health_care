# healthy care

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
  - [Install Dependencies](#install-dependencies)
  - [Launch Development Server](#launch-development-server)
  - [Configure Environment Variables](#configure-environment-variables)
  - [Initialize Database](#initialize-database)
  - [Seed Data](#seed-data)
- [Additional Tools](#additional-tools)
  - [Package Management](#package-management)
  - [Database Migrations](#database-migrations)

---

## Prerequisites
- Docker
- Python 3.9

## Quick Start


### Configure Environment Variables
```bash
# Copy the example .env file and fill in the required configurations.
cp .env.example .env
```


### Install Dependencies
```bash
# This command installs all project dependencies inside a Docker container.
docker-compose run app poetry install
```

### Launch Development Server
```bash
# Starts the development server in detached mode.
docker-compose up -d
```

### Initialize Database
```bash
# This command migrates the database to the latest version.
docker-compose run app poetry run alembic upgrade head
```

### Seed Data
Navigate to the API at http://localhost:8000/docs and run `/api/v1/system/seeding_data`.
> **Note**: The `master_key` value is obtained from the `.env` file.

## Additional Tools
- **phpMyAdmin**: Accessible at http://localhost:20080/
- **Swagger Docs**: Accessible at http://localhost:8000/docs

### Package Management
To add a new package:
```bash
docker-compose exec app poetry add <new_package>
```
To export packages to a requirements file:
```bash
docker-compose exec app poetry export -f requirements.txt --without-hashes --output requirements.txt
```

### Database Migrations
1. **Generate New Migrations**
    ```bash
    docker-compose exec app poetry run alembic revision --autogenerate -m "<migration_message>"
    ```
2. **Upgrade Database**
    ```bash
    docker-compose exec app poetry run alembic upgrade head
    ```
3. **Downgrade Database**
    ```bash
    docker-compose exec app poetry run alembic downgrade -1
    ```