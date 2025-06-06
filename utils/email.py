import os
from jinja2 import Environment, FileSystemLoader
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from models import db, NotificationLog

try:
    from mjml import mjml2html
    def compile_mjml(content: str) -> str:
        return mjml2html(content).html
except Exception:  # pragma: no cover - mjml is optional
    def compile_mjml(content: str) -> str:
        return content


template_env = Environment(loader=FileSystemLoader('templates'))


def send_email(to_email: str, subject: str, template_name: str, context: dict) -> None:
    template = template_env.get_template(template_name)
    rendered = template.render(**context)
    if template_name.endswith('.mjml'):
        html_content = compile_mjml(rendered)
    else:
        html_content = rendered

    message = Mail(
        from_email=os.environ.get('EMAIL_FROM_ADDRESS'),
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        raise RuntimeError('SENDGRID_API_KEY is not configured')
    sg = SendGridAPIClient(api_key)
    sg.send(message)

    log = NotificationLog(recipient=to_email, subject=subject, body=html_content)
    db.session.add(log)
    db.session.commit()
