import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.services.email_templates import (
    welcome_verification_email_html,
    welcome_verification_email_text,
    login_notification_email_html,
    login_notification_email_text,
    account_deleted_email_html,
    account_deleted_email_text,
    password_reset_requested_email_html,
    password_reset_requested_email_text,
    password_changed_email_html,
    password_changed_email_text,
)


class EmailService:
    def __init__(self) -> None:
        self.client = boto3.client("ses", region_name=settings.SES_REGION)

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
    ) -> bool:
        try:
            self.client.send_email(
                Source=f"{settings.SES_FROM_NAME} <{settings.SES_FROM_EMAIL}>",
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {
                        "Data": subject,
                        "Charset": "UTF-8",
                    },
                    "Body": {
                        "Html": {
                            "Data": html_body,
                            "Charset": "UTF-8",
                        },
                        "Text": {
                            "Data": text_body,
                            "Charset": "UTF-8",
                        },
                    },
                },
            )
            print(f"SES email sent successfully to {to_email}")
            return True

        except (BotoCoreError, ClientError) as exc:
            print(f"SES email send failed to {to_email}: {exc}")
            return False

    def send_verification_email(
        self,
        to_email: str,
        full_name: str,
        token: str,
    ) -> bool:
        return self.send_email(
            to_email=to_email,
            subject="Welcome to Firefighter Data Hub - Please Verify Your Email Address",
            html_body=welcome_verification_email_html(full_name, token),
            text_body=welcome_verification_email_text(full_name, token),
        )

    def send_login_notification(
        self,
        to_email: str,
        full_name: str,
    ) -> bool:
        return self.send_email(
            to_email=to_email,
            subject="Firefighter Data Hub - Login Notification",
            html_body=login_notification_email_html(full_name),
            text_body=login_notification_email_text(full_name),
        )

    def send_account_deleted_notification(
        self,
        to_email: str,
        full_name: str,
    ) -> bool:
        return self.send_email(
            to_email=to_email,
            subject="Firefighter Data Hub - Account Deletion Confirmation",
            html_body=account_deleted_email_html(full_name),
            text_body=account_deleted_email_text(full_name),
        )
    
    def send_password_reset_requested_notification(
        self,
        to_email: str,
        full_name: str,
    ) -> bool:
        return self.send_email(
            to_email=to_email,
            subject="Firefighter Data Hub - Password Change Request Initiated",
            html_body=password_reset_requested_email_html(full_name),
            text_body=password_reset_requested_email_text(full_name),
        )

    def send_password_changed_notification(
        self,
        to_email: str,
        full_name: str,
    ) -> bool:
        return self.send_email(
            to_email=to_email,
            subject="Firefighter Data Hub - Password Updated Successfully",
            html_body=password_changed_email_html(full_name),
            text_body=password_changed_email_text(full_name),
        )


email_service = EmailService()