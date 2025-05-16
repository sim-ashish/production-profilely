from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from settings import settings
from fastapi import BackgroundTasks
import asyncio

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_USERNAME,
    MAIL_STARTTLS=True,    
    MAIL_SSL_TLS=False, 
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER='templates'
)

async def send_email_async(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
        subtype='html',
    )
    
    fm = FastMail(conf)
    await fm.send_message(message, template_name='verify_email_template.html')


def send_email_background(subject: str, email_to: str, template_name: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
        subtype='html',
    )
    fm = FastMail(conf)

    asyncio.run(fm.send_message(message, template_name=f'{template_name}'))