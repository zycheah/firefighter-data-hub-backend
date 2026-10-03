# Deployment Guide

This guide covers deploying the API from this repository to an Ubuntu server on Amazon EC2. The same steps apply to any Linux server.

| Item | Setup |
|---|---|
| Server | Ubuntu on Amazon EC2 |
| App directory | `/home/ubuntu/firefighter-backend` |
| Process manager | systemd service `firefighter` |
| App server | uvicorn on port 8000 |
| Database | Amazon RDS for PostgreSQL |
| Email | Amazon SES (`us-east-1`) |

> **Existing production server.** The server currently in production was deployed from the original combined repository, before the code was split. Its app directory is `/home/ubuntu/g_sb_2/Backend`, and its systemd service points there. Use that path in the commands below until the server is redeployed from this repository.

---

## 1. AWS prerequisites

1. **RDS PostgreSQL instance.** The EC2 instance's security group must be allowed to reach it on port 5432.
2. **SES sender.** Verify the sender address or domain used in `SES_FROM_EMAIL`. While SES is in sandbox mode, recipient addresses must also be verified. Request production access to email any user.
3. **IAM role for EC2.** Attach a role with `ses:SendEmail` and `ses:SendRawEmail` (and S3 permissions if `/files` is used). With a role, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are not needed.
4. **Security group.** Allow inbound SSH (22) from trusted addresses only, and HTTP/HTTPS (80/443). Allow port 8000 only until Nginx is in place.

---

## 2. First-time server setup

### Step 1: Connect to the server

```bash
chmod 400 /path/to/key.pem
ssh -i /path/to/key.pem ubuntu@<SERVER_HOST>
```

### Step 2: Install system packages

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git postgresql-client
```

### Step 3: Get the code

```bash
cd /home/ubuntu
git clone <repository-url> firefighter-backend
cd firefighter-backend
```

### Step 4: Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Create the production `.env`

```bash
cp .env.example .env
nano .env
```

Set the RDS `DATABASE_URL`, strong values for `SECRET_KEY` and `EMAIL_TOKEN_SECRET`, the SES sender, and `CORS_ORIGINS` set to the web dashboard's URL. Leave the AWS key variables empty when the server has an IAM role. Restrict the file:

```bash
chmod 600 .env
```

### Step 6: Apply database migrations

```bash
alembic upgrade head
```

On a new database, the migrations do not create the `users_researcher` table that web dashboard login needs. See item F2 in [ROADMAP.md](ROADMAP.md).

### Step 7: Create the systemd service

```bash
sudo nano /etc/systemd/system/firefighter.service
```

```ini
[Unit]
Description=Firefighter Safety Data Hub API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/firefighter-backend
EnvironmentFile=/home/ubuntu/firefighter-backend/.env
ExecStart=/home/ubuntu/firefighter-backend/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Step 8: Start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable firefighter
sudo systemctl start firefighter
sudo systemctl status firefighter
```

### Step 9: Check the health endpoint

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok"}
```

---

## 3. Deploying an update

```bash
ssh -i /path/to/key.pem ubuntu@<SERVER_HOST>
cd /home/ubuntu/firefighter-backend

git pull
source .venv/bin/activate
pip install -r requirements.txt   # only needed when requirements.txt changed
alembic upgrade head              # only needed when a migration was added

sudo systemctl restart firefighter
curl http://localhost:8000/api/v1/health
```

To roll back, check out the previous commit (`git checkout <commit>`), downgrade any migration that was added (`alembic downgrade -1`), and restart the service.

---

## 4. Logs and troubleshooting

| Task | Command |
|---|---|
| Last 100 log lines | `sudo journalctl -u firefighter -n 100 --no-pager` |
| Follow logs live | `sudo journalctl -u firefighter -f` |
| Email-related logs | `sudo journalctl -u firefighter -n 300 --no-pager \| grep -i "ses\|email"` |
| Service status | `sudo systemctl status firefighter` |
| Current migration | `alembic current` |
| Connect to the database | `psql -h <DB_HOST> -U <DB_USER> -d <DB_NAME>` |

| Symptom | Likely cause |
|---|---|
| Service fails at start with a validation error | A required variable is missing from `.env` |
| `DATABASE_URL ... is not set` when running Alembic | Command run outside the project folder, or `.env` missing |
| Emails not delivered, `InvalidClientTokenId` in logs | Invalid AWS credentials or no IAM role attached |
| Emails not delivered, `MessageRejected` | Sender not verified, or SES still in sandbox mode |
| Web dashboard shows CORS errors | Dashboard URL missing from `CORS_ORIGINS` |

---

## 5. HTTPS with Nginx (recommended)

### Step 1: Point a domain at the server

Create a DNS `A` record, for example `api.<your-domain>`, with the server's public IP address.

### Step 2: Install Nginx and add a site

```bash
sudo apt install -y nginx
sudo nano /etc/nginx/sites-available/firefighter-api
```

```nginx
server {
    listen 80;
    server_name api.<your-domain>;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/firefighter-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 3: Add a certificate

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.<your-domain>
```

### Step 4: Finish

1. Change uvicorn to listen on `127.0.0.1` in the systemd service and restart it.
2. Remove port 8000 from the security group.
3. Update the API address in the mobile app (`app_config.dart`) and web dashboard (`VITE_API_BASE_URL`) to `https://api.<your-domain>`.

---

## 6. Post-deployment checks

Run these after each release. Use a test account.

**API**
- [ ] `GET /api/v1/health` returns `{"status":"ok"}`

**Accounts (mobile app)**
- [ ] Register a new user: the user appears in `users` and `user_profiles`, and a verification email arrives
- [ ] Verify the email with the token, then log in: a login notification email arrives
- [ ] Forgot password: request and confirm emails arrive, and the new password works

**Data submission (mobile app)**
- [ ] Log an event and submit PPE: rows appear in `log_events` and `ppe_table`
- [ ] Submit a smoke sampler with one sample and with several samples
- [ ] Upload a location and open Location History: the latest points appear

**Web dashboard**
- [ ] Log in as a researcher, open the dashboard, the GPS table and the event table
- [ ] Download both CSV exports

**Account deletion**
- [ ] Delete the test account from Settings: a confirmation email arrives and the user's rows are removed
