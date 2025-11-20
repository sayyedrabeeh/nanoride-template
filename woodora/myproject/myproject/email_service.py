import resend
from django.conf import settings

def send_otp_email(email, otp):
    """
    Sends OTP email using Resend API.
    Returns True if success, False if failed.
    """
    try:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [email],
            "subject": "Your OTP Code",
            "text": f"Your OTP code is {otp}. It expires in 5 minutes."
        })
        return True
    except Exception as e:
        print("RESEND EMAIL ERROR:", e)
        return False


def send_email(to_email, subject, html_content):
    try:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        })
        return True
    except Exception as e:
        print("Resend Email Error:", e)
        return False