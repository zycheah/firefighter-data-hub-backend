# Roadmap and Known Issues

This document lists known issues and planned work across the whole system. Items are grouped by priority. Each item names the repository it affects.

---

## 1. Security (high priority)

| # | Item | Repository |
|---|---|---|
| S1 | `POST /api/v1/auth/forgot-password/confirm` sets a new password from an email address alone. It should require the signed token sent by email. | backend |
| S2 | `GET /api/v1/web_api/data/tabledata` returns GPS data without authentication. Add the same researcher check used by the other web endpoints. | backend |
| S3 | The API is served over plain HTTP. Put it behind Nginx with HTTPS (see `docs/DEPLOYMENT.md` in the backend repository) and update both clients to the HTTPS address. | backend, frontend |
| S4 | `CORS_ORIGINS` defaults to `*`. Restrict it to the web dashboard's URL in production. | backend |
| S5 | Use an EC2 IAM role for SES and S3 instead of access keys, and keep secrets in AWS Secrets Manager or Parameter Store. | backend |
| S6 | Add role-based access control (firefighter, chief, researcher, admin) to endpoints that return data. | backend |
| S7 | `POST /api/v1/web_api/auth/register` is open: anyone can create a researcher account and then view and export data. Add an approval or invitation step. | backend |
| S8 | The production database accepts connections from the public internet. Restrict its security group to the API server and known addresses, and rotate the database password. | backend |

---

## 2. Functional gaps

| # | Item | Repository |
|---|---|---|
| F1 | The web dashboard calls endpoints that the API does not provide yet: `/web_api/auth/refresh`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/resend-verification`, `/contact` and `/account-requests`. The related pages (forgot password, contact, account request, silent token refresh) do not work until these exist. | backend |
| F2 | The `users_researcher` table is not created by the Alembic migrations. Add a migration so that a fresh database supports web dashboard login. | backend |
| F3 | `app/core/s3.py` reads `AWS_REGION`, `S3_BUCKET_NAME` and the AWS keys, but these settings are not defined in `app/core/config.py`, so the `/files` endpoints fail. Add the settings or remove the endpoints. | backend |
| F4 | The legacy `location_entries` table and `app/api/v1/endpoints/locations.py` are no longer used. Remove them in a migration once confirmed. | backend |
| F5 | The web dashboard covers GPS and event data only. PPE and smoke sampler data cannot yet be viewed or exported. | backend, frontend |

---

## 3. Developer experience

| # | Item | Repository |
|---|---|---|
| D1 | No automated tests. Add `pytest` tests for the API (using a test database) and widget tests for the main mobile flows. | both |
| D2 | No CI. Add a pipeline that runs linting (`ruff`, `eslint`, `flutter analyze`), tests and builds on each pull request. | both |
| D3 | The mobile app's API address is a compile-time constant. Move it to `--dart-define` so that builds can target different environments without code changes. | frontend |
| D4 | The local backend port differs between clients (8080) and the API (8000). Standardise on 8000. | frontend |
| D5 | Add a `docker-compose.yml` that starts PostgreSQL and the API together for local development. | backend |
| D6 | Android builds, including debug builds, fail when `android/key.properties` is missing, because `android/app/build.gradle.kts` reads the signing values without a fallback. Fall back to debug signing when the file is absent. | frontend |
| D7 | `npm run lint` in `web/` reports two errors (`src/vite-env.d.ts` and `src/pages/ProfilePage.tsx`). The build is not affected. | frontend |
| D8 | In `mobile/lib/config/app_config.dart`, `localLanOverride` is set to a fixed LAN address, which overrides the emulator and simulator addresses whenever `useAwsBackend` is `false`. Default it to an empty string. | frontend |

---

## 4. Production readiness

| # | Item | Repository |
|---|---|---|
| P1 | Deploy the API as a Docker image (ECR) on ECS behind an Application Load Balancer instead of a single EC2 instance. | backend |
| P2 | Add CloudWatch logs, metrics and alarms. | backend |
| P3 | Host the web dashboard build (for example S3 + CloudFront). | frontend |
| P4 | Before publishing the mobile app: finalise the app name and package ID, publish a privacy policy, complete the Google Play Data Safety form and the background-location justification. | frontend |

---

## 5. Future features

- AI-assisted event logging from voice or chat. The interview script is drafted in `mobile/lib/doc/promt.md` in the frontend repository, with the question set in `mobile/lib/doc/log_questions.json`.
- Lab result ingestion from CSV and chain-of-custody tracking for passive samplers.
- Research dashboards with filtering, and CSV/JSON export of all data types.
- Expansion of the glove fit recommendation module.
- Integration with fire reporting standards (NFIRS/NERIS). Reference notes are in `docs/ImageTrendFeatures.txt` in the frontend repository.
