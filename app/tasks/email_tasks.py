import os
import re

import resend
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.integrations.queue.celery_bootstrap import celery_app
from app.db.session import SessionLocal
from app.modules.orders.infrastructure.repository import OrderRepository


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

# Resend SDK setup
resend.api_key = settings.resend_api_key

FROM_EMAIL = settings.mail_from  # e.g. "Meeps Store <noreply@meepsstore.me>"


def _extract_email_address(value: str) -> str:
    match = re.search(r"<([^>]+)>", value or "")
    if match:
        return match.group(1).strip()
    return (value or "").strip()


ADMIN_EMAIL = settings.admin_email or _extract_email_address(settings.mail_from)


def _send_email_util(recipient: str, subject: str, body: str, is_html: bool = True) -> dict:
    payload = {
        "from": FROM_EMAIL,
        "to": [recipient],
        "subject": subject,
    }

    if is_html:
        payload["html"] = body
    else:
        payload["text"] = body

    return resend.Emails.send(payload)


@celery_app.task(
    name="send_welcome_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_welcome_email(self, user_email: str, full_name: str):
    subject = "Welcome to Meeps Store!"
    template = env.get_template("emails/welcome.html")
    html_content = template.render(
        full_name=full_name,
        user_email=user_email,
    )
    _send_email_util(user_email, subject, html_content, is_html=True)
    return f"Welcome email sent to {user_email}"


@celery_app.task(
    name="send_password_reset_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_password_reset_email(self, user_email: str, full_name: str, reset_url: str):
    subject = "Reset your Meeps Store password"
    template = env.get_template("emails/password_reset.html")
    html_content = template.render(
        full_name=full_name,
        user_email=user_email,
        reset_url=reset_url,
    )
    _send_email_util(user_email, subject, html_content, is_html=True)
    return f"Password reset email sent to {user_email}"


@celery_app.task(
    name="send_order_confirmation_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_order_confirmation_email(self, user_email: str, order_id: int, total_amount: float):
    subject = f"Order confirmed - #{order_id}"
    template = env.get_template("emails/order_confirmation.html")
    html_content = template.render(
        order_id=order_id,
        total_amount=total_amount,
    )
    _send_email_util(user_email, subject, html_content, is_html=True)
    return f"Confirmation sent to {user_email}"


@celery_app.task(
    name="notify_admin_new_order",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def notify_admin_new_order(
    self,
    order_id: int,
    total: float | None = None,
    items_count: int | None = None,
):
    db = SessionLocal()
    try:
        print(f"notify_admin_new_order recipient={ADMIN_EMAIL}")
        order_repo = OrderRepository(db)
        context = order_repo.get_admin_notification_context(order_id)
        if not context:
            return f"Order #{order_id} not found"

        subject = f"New order received - #{order_id}"
        template = env.get_template("emails/admin_new_order.html")
        html_content = template.render(**context)
        _send_email_util(ADMIN_EMAIL, subject, html_content, is_html=True)
        return f"Admin notified for order #{order_id}"
    finally:
        db.close()


@celery_app.task(
    name="send_shipping_update_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_shipping_update_email(self, user_email: str, order_id: int, new_status: str):
    subject = f"Shipping update - Order #{order_id}"
    template = env.get_template("emails/shipping_update.html")
    html_content = template.render(
        user_email=user_email,
        order_id=order_id,
        new_status=new_status,
    )
    _send_email_util(user_email, subject, html_content, is_html=True)
    return f"Shipping update sent to {user_email}"