# API Reference

All endpoints accept and return JSON unless stated otherwise. Interactive documentation, generated from the code, is available at `/docs` (Swagger UI) and `/redoc` on any running instance.

**Authentication.** Endpoints marked 🔒 require the header:

```
Authorization: Bearer <access_token>
```

The token is returned by the login endpoint of the matching API (mobile or web). Mobile tokens and researcher tokens are issued for different account tables and are not interchangeable.

---

## Mobile API — prefix `/api/v1`

### Health

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | – | Returns `{"status": "ok"}` |

### Authentication — `/auth`

| Method | Path | Auth | Body | Description |
|---|---|---|---|---|
| POST | `/auth/register` | – | `UserRegisterDTO` | Creates the user and profile, emails a verification token |
| POST | `/auth/verify-email` | – | `{ token }` | Marks the email address as verified |
| POST | `/auth/resend-verification` | – | `{ email }` | Sends a new verification token |
| POST | `/auth/login` | – | `{ email, password }` | Returns an access token. Fails until the email is verified |
| POST | `/auth/refresh` | 🔒 | – | Issues a new token and invalidates the old one |
| GET | `/auth/me` | 🔒 | – | Returns the current user and profile |
| POST | `/auth/forgot-password/request` | – | `{ email }` | Emails a password change notice |
| POST | `/auth/forgot-password/confirm` | – | `{ email, newPassword }` | Sets a new password and sends a confirmation email |
| POST | `/auth/password-reset` | 🔒 | `{ password, newPassword }` | Changes the password of the signed-in user |
| DELETE | `/auth/delete-account` | 🔒 | `{ password }` | Deletes the account and all of its data, then sends a confirmation email |
| GET | `/auth/test` | – | – | Development test route |

**`UserRegisterDTO` fields:** `full_name`, `email`, `password`, `role` (default `firefighter`), `phoneNumber`, `gender`, `race`, `ethnicity`, `year_of_birth`, `height_cm`, `weight_kg`, `dominant_hand`, `Years_of_experience`, `firefighter_status`, `type_of_firefighter`, `firefighter_station_name`, `city`, `state`.

### Location — `/locationEntries`

| Method | Path | Auth | Body / query | Description |
|---|---|---|---|---|
| POST | `/locationEntries/` | 🔒 | Array of `{ latitude, longitude, timestamp?, locationTimestamp?, accuracy?, altitude? }` | Stores a batch of GPS points |
| GET | `/locationEntries/last` | 🔒 | `?limit=10` (1–100) | Returns the user's most recent points |

### Exposure data — `/data-transfer` and `/smokeSampler`

| Method | Path | Auth | Body | Description |
|---|---|---|---|---|
| POST | `/data-transfer/logevent` | 🔒 | `{ event_date, event_address, is_same_ppe }` | Logs a fire event and returns its `event_id` |
| POST | `/data-transfer/ppe` | 🔒 | `{ event_id?, helmet_id, hood_id, face_mask_id, scba_id, glove_id, boot_id, bunker_coat_id, bunker_pants_id, is_ppe_updated }` | Stores the PPE item IDs, optionally linked to an event. All fields are optional |
| POST | `/smokeSampler/` | 🔒 | `{ samples: [{ chemical_name, percentage_proportion }] }` (1–50 samples, 0–100 %) | Stores one smoke sampler submission with its samples |

### Files — `/files`

These endpoints do not work yet, because their S3 settings are not defined in the application settings. See item F3 in [ROADMAP.md](ROADMAP.md).

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/files/upload` | 🔒 | Multipart upload to S3, metadata stored in `uploaded_files` |
| GET | `/files` | 🔒 | Lists the user's uploaded files |

---

## Web API — prefix `/api/v1/web_api`

### Authentication — `/auth`

| Method | Path | Auth | Body | Description |
|---|---|---|---|---|
| POST | `/auth/register` | – | `{ first_name, last_name, university_email, personal_email?, phoneNumber?, role, password }` | Creates a researcher account |
| POST | `/auth/login` | – | `{ email, password }` | Returns an access token |
| GET | `/auth/me` | 🔒 | – | Returns the researcher profile |
| PUT | `/auth/me` | 🔒 | `{ first_name?, last_name?, personal_email?, phoneNumber? }` | Updates the profile |
| POST | `/auth/password-reset` | 🔒 | `{ password, newPassword }` | Changes the password |

### Dashboard and data

| Method | Path | Auth | Query | Description |
|---|---|---|---|---|
| GET | `/dashboard/summary` | 🔒 | – | Counts of firefighters, chiefs and fire stations |
| GET | `/data/tabledata` | – | `limit`, `page` (both required) | Paginated GPS points from `locations`. Not yet protected, see item S2 in [ROADMAP.md](ROADMAP.md) |
| GET | `/table/export-csv` | 🔒 | – | All GPS points as a CSV download |
| GET | `/table/eventdata` | 🔒 | `limit`, `page` (both required) | Paginated fire events |
| GET | `/table/export-event-data` | 🔒 | – | All fire events as a CSV download |

---

## Errors

Errors use FastAPI's standard format:

```json
{ "detail": "Invalid or expired token" }
```

| Status | Meaning |
|---|---|
| 400 | Invalid request (for example, email already registered) |
| 401 | Missing, invalid or replaced token, or wrong password |
| 403 | Email address not verified |
| 404 | Resource not found |
| 422 | Request body failed validation |
| 500 | Unexpected server error |
