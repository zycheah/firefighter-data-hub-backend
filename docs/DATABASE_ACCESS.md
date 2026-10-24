# Database Access

How to connect to the project's PostgreSQL database with [DBeaver](https://dbeaver.io/).

## Credentials

The host, database name, username and password are in the handover package:
`handover/documents/technical/Access_Details.md`, section **RDS / PostgreSQL**.

They are not stored in this repository.

## Which database to use

| Task | Database |
|---|---|
| View or export data | Production, read-only |
| Run the apps against the deployed API | Production (nothing to set up) |
| Develop backend changes | Local |

The production database holds real personal data, and changes to it are permanent. Develop and test on a local database.

## Connect to production

1. In DBeaver, choose **Database → New Database Connection → PostgreSQL**.
2. Enter the host, database, username and password from `Access_Details.md`. The port is `5432`.
3. On the **SSH** tab, tick **Use SSH Tunnel** and connect through the API server: host `<EC2 public IP>`, port `22`, user `ubuntu`, authentication **Public Key** with the EC2 key pair file from the handover package. The database only accepts connections from the API server, so a direct connection from a laptop is refused.
4. On the **General** tab, set **Connection type** to **Production** and tick **Read-only connection**.
5. Click **Test Connection**, then **Finish**.

The tables are under **Schemas → public → Tables**.

## Tables

| Table | Contents |
|---|---|
| `users`, `user_profiles` | Firefighter accounts and profile details |
| `users_researcher` | Researcher accounts for the web dashboard |
| `location_entries`, `locations` | GPS positions from the mobile app |
| `log_events` | Fire events |
| `ppe_table` | Protective equipment IDs |
| `smoke_sampler_submissions`, `smoke_sampler_samples` | Smoke sampler results |
| `uploaded_files` | Metadata for uploaded files |
| `alembic_version` | Migration version. Do not edit. |

To export data, right-click a table and choose **Export Data**.

## Alembic

Alembic creates and changes the database structure. It is required: the API does not create tables itself.

| Situation | Command |
|---|---|
| Viewing data or running the API | None |
| New, empty database | `alembic upgrade head` |
| After pulling a new migration | `alembic upgrade head` |
| After changing a model | `alembic revision --autogenerate -m "describe the change"`, then `alembic upgrade head` |

Do not change tables by hand. Test a migration locally, then apply it to production during a deployment (see [DEPLOYMENT.md](DEPLOYMENT.md)).

## Local database

Needed only when developing backend changes.

```bash
createdb firefighter
alembic upgrade head
```

Set `DATABASE_URL` in `.env` to `postgresql+psycopg2://<LOCAL_USER>@localhost:5432/firefighter`, then connect DBeaver to host `localhost`, port `5432`, database `firefighter`.

Known issue: the migrations do not create `users_researcher`, so web dashboard login fails on a new database.
