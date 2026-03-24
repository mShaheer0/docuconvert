import smtplib
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["contact"])


class ContactRequest(BaseModel):
    name: str
    email: str
    message: str

    @staticmethod
    def validate_email(email: str) -> bool:
        """Simple email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


def send_email(name: str, email: str, message: str) -> bool:
    """
    Send contact form email using SMTP.
    Uses environment variables for sensitive credentials.
    """
    try:
        # Email configuration (use environment variables for production)
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "memershaheer@gmail.com")
        sender_password = os.getenv("SENDER_PASSWORD", "")
        recipient_email = "memershaheer@gmail.com"

        if not sender_password:
            print("Email service not configured: missing SENDER_PASSWORD")
            return False

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New Contact Form Submission from {name}"
        msg["From"] = sender_email
        msg["To"] = recipient_email

        # Plain text version
        text_content = f"""
New contact form submission:

Name: {name}
Email: {email}
Message:
{message}
"""

        # HTML version
        html_content = f"""
<html>
  <body>
    <h2>New Contact Form Submission</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Message:</strong></p>
    <p>{message.replace(chr(10), '<br>')}</p>
  </body>
</html>
"""

        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")

        msg.attach(part1)
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        return True

    except smtplib.SMTPException as e:
        print(f"SMTP error sending email: {e}")
        return False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


@router.post("/contact")
async def contact(request: ContactRequest):
    """
    Handle contact form submissions.
    Sends an email to the configured recipient.
    """
    try:
        # Validate email format
        if not ContactRequest.validate_email(request.email):
            raise HTTPException(
                status_code=400,
                detail="Invalid email address format.",
            )

        # Validate message content
        if not request.name or not request.message:
            raise HTTPException(
                status_code=400,
                detail="Name and message are required.",
            )

        if not os.getenv("SENDER_PASSWORD", ""):
            raise HTTPException(
                status_code=500,
                detail="Email service is not configured. Set SENDER_PASSWORD and restart the server.",
            )

        success = send_email(request.name, request.email, request.message)

        if success:
            return {
                "status": "success",
                "message": "Your message has been sent successfully. We'll get back to you soon!",
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send message. Please try again later.",
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Contact form error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request.",
        )
