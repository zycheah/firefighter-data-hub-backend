def welcome_verification_email_html(full_name: str, token: str) -> str:
    display_name = full_name if full_name else "Valued User"

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">
        <h2>Firefighter Data Hub</h2>
        <h3>Firefighter Safety Data Hub</h3>

        <p><strong>Welcome to Firefighter Data Hub!</strong></p>

        <p>Dear {display_name},</p>

        <p>
          Thank you for creating an account with Firefighter Data Hub. We are excited to have you join
          our community dedicated to improving firefighter safety through secure exposure event logging,
          PPE tracking, and research-driven data management.
        </p>

        <p>
          To complete your registration and ensure the security of your account,
          please verify your email address using the verification token below:
        </p>

        <p style="font-size: 18px; font-weight: bold; word-break: break-all;
                  background: #f4f4f4; padding: 14px; border-radius: 6px;">
          {token}
        </p>

        <p>
          Open the Firefighter Data Hub app, go to the Verify Email screen,
          and paste this token.
        </p>

        <p><strong>Please Note:</strong> This verification token will expire in 24 hours for your security.</p>

        <p>Once your email is verified, you will be able to:</p>
        <ul>
          <li>Access your secure Firefighter Data Hub account</li>
          <li>Log and manage firefighter exposure events</li>
          <li>Track PPE-related data and safety records</li>
          <li>View and manage your profile and project-related information</li>
        </ul>

        <p>
          If you did not create an account with Firefighter Data Hub, please disregard this email.
          No action is required.
        </p>

        <p>
          Best regards,<br>
          The Firefighter-DataHub Team
        </p>

        <p>Iowa State University</p>

        <p style="font-size: 12px; color: #666;">
          This is an automated message. Please do not reply directly to this email.
        </p>
      </body>
    </html>
    """


def welcome_verification_email_text(full_name: str, token: str) -> str:
    display_name = full_name if full_name else "Valued User"

    return f"""
Firefighter Data Hub
Firefighter Safety Data Hub

Welcome to Firefighter Data Hub!

Dear {display_name},

Thank you for creating an account with Firefighter Data Hub.

Please verify your email address using this verification token:

{token}

Open the Firefighter Data Hub app, go to the Verify Email screen, and paste this token.

This verification token will expire in 24 hours.

Best regards,
The Firefighter-DataHub Team

Iowa State University

This is an automated message. Please do not reply directly to this email.
""".strip()


def login_notification_email_html(full_name: str) -> str:
    display_name = full_name if full_name else "User"

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">
        <h2>Firefighter Data Hub</h2>
        <h3>Login Notification</h3>

        <p>Dear {display_name},</p>

        <p>Your Firefighter Data Hub account was successfully signed in.</p>

        <p>
          If this was you, no action is required.
          If you did not sign in, please change your password immediately.
        </p>

        <p>
          Best regards,<br>
          The Firefighter-DataHub Team
        </p>

        <p>Iowa State University</p>

        <p style="font-size: 12px; color: #666;">
          This is an automated message. Please do not reply directly to this email.
        </p>
      </body>
    </html>
    """


def login_notification_email_text(full_name: str) -> str:
    display_name = full_name if full_name else "User"

    return f"""
Firefighter Data Hub

Dear {display_name},

Your Firefighter Data Hub account was successfully signed in.

If this was you, no action is required.
If you did not sign in, please change your password immediately.

Best regards,
The Firefighter-DataHub Team

Iowa State University
""".strip()


def account_deleted_email_html(full_name: str) -> str:
    display_name = full_name if full_name else "User"

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">
        <h2>Firefighter Data Hub</h2>
        <h3>Account Deletion Confirmation</h3>

        <p>Dear {display_name},</p>

        <p>
          Your Firefighter Data Hub account deletion request has been completed.
          Your account and associated profile information have been removed from the system.
        </p>

        <p><strong>Important:</strong> This action cannot be undone.</p>

        <p>
          If you did not request this account deletion, please contact the project support team immediately.
        </p>

        <p>
          Best regards,<br>
          The Firefighter-DataHub Team
        </p>

        <p>Iowa State University</p>

        <p style="font-size: 12px; color: #666;">
          This is an automated message. Please do not reply directly to this email.
        </p>
      </body>
    </html>
    """


def account_deleted_email_text(full_name: str) -> str:
    display_name = full_name if full_name else "User"

    return f"""
Firefighter Data Hub
Account Deletion Confirmation

Dear {display_name},

Your Firefighter Data Hub account deletion request has been completed.
Your account and associated profile information have been removed from the system.

Important: This action cannot be undone.

If you did not request this account deletion, please contact the project support team immediately.

Best regards,
The Firefighter-DataHub Team

Iowa State University
""".strip()

def password_reset_requested_email_html(full_name: str) -> str:
    display_name = full_name if full_name else "User"

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">
        <h2>Firefighter Data Hub</h2>
        <h3>Password Change Request Initiated</h3>

        <p>Dear {display_name},</p>

        <p>
          We received a request to change the password for your Firefighter Data Hub account.
        </p>

        <p>
          If this request was made by you, you can continue setting your new password in the app.
        </p>

        <p>
          If you did not request this password change, please contact support immediately
          and review your account security.
        </p>

        <p>
          Best regards,<br>
          The Firefighter-DataHub Team
        </p>

        <p>Iowa State University</p>

        <p style="font-size: 12px; color: #666;">
          This is an automated message. Please do not reply directly to this email.
        </p>
      </body>
    </html>
    """


def password_reset_requested_email_text(full_name: str) -> str:
    display_name = full_name if full_name else "User"

    return f"""
Firefighter Data Hub
Password Change Request Initiated

Dear {display_name},

We received a request to change the password for your Firefighter Data Hub account.

If this request was made by you, you can continue setting your new password in the app.

If you did not request this password change, please contact support immediately and review your account security.

Best regards,
The Firefighter-DataHub Team

Iowa State University
""".strip()


def password_changed_email_html(full_name: str) -> str:
    display_name = full_name if full_name else "User"

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">
        <h2>Firefighter Data Hub</h2>
        <h3>Password Updated Successfully</h3>

        <p>Dear {display_name},</p>

        <p>
          Your Firefighter Data Hub account password has been updated successfully.
        </p>

        <p>
          If you made this change, no further action is required.
        </p>

        <p>
          If you did not change your password, please contact support immediately.
        </p>

        <p>
          Best regards,<br>
          The Firefighter-DataHub Team
        </p>

        <p>Iowa State University</p>

        <p style="font-size: 12px; color: #666;">
          This is an automated message. Please do not reply directly to this email.
        </p>
      </body>
    </html>
    """


def password_changed_email_text(full_name: str) -> str:
    display_name = full_name if full_name else "User"

    return f"""
Firefighter Data Hub
Password Updated Successfully

Dear {display_name},

Your Firefighter Data Hub account password has been updated successfully.

If you made this change, no further action is required.

If you did not change your password, please contact support immediately.

Best regards,
The Firefighter-DataHub Team

Iowa State University
""".strip()