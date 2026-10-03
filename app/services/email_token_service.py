from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings


class EmailTokenService:
    def __init__(self) -> None:
        self.serializer = URLSafeTimedSerializer(settings.EMAIL_TOKEN_SECRET)

    def generate_verify_email_token(self, user_id: str, email: str) -> str:
        return self.serializer.dumps(
            {
                "sub": user_id,
                "email": email,
                "purpose": "verify_email",
            },
            salt="verify-email",
        )

    def verify_email_token(self, token: str, max_age_seconds: int = 86400) -> dict:
        return self.serializer.loads(
            token,
            salt="verify-email",
            max_age=max_age_seconds,
        )


email_token_service = EmailTokenService()