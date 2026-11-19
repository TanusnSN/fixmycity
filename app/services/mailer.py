import json
import threading
import urllib.request

from .. import config


def send_email(to: str, subject: str, body: str) -> bool:
    """Send an email through Brevo. With no BREVO_API_KEY, print it in the terminal (dev mode)."""
    if not config.BREVO_API_KEY or not config.MAIL_FROM_EMAIL:
        print(f"\n--- EMAIL (dev mode, not sent) ---\nTo: {to}\nSubject: {subject}\n{body}\n----------------------------------\n", flush=True)
        return True
    payload = {
        "sender": {"name": config.MAIL_FROM_NAME, "email": config.MAIL_FROM_EMAIL},
        "to": [{"email": to}],
        "subject": subject,
        "textContent": body,
    }
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode(),
        headers={
            "api-key": config.BREVO_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "FixMyCity/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except Exception as exc:  # an email problem must never crash a request
        print(f"Email to {to} failed: {exc}", flush=True)
        return False


def send_email_async(to: str, subject: str, body: str) -> None:
    threading.Thread(target=send_email, args=(to, subject, body), daemon=True).start()