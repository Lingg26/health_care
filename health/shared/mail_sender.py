from email_validator import EmailNotValidError, validate_email
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from health.core import settings


conf = ConnectionConfig(
   MAIL_USERNAME=settings.MAIL_USERNAME,
   MAIL_FROM=settings.MAIL_USERNAME,
   MAIL_PASSWORD=settings.MAIL_PASSWORD,
   MAIL_PORT=settings.MAIL_PORT,
   MAIL_SERVER="smtp.gmail.com",
   MAIL_TLS=True,
   MAIL_SSL=False
)
async def Sender(receiver_email,subject ):
    template = """
            <html>
            <body>


    <p>Hi !!!
            <br>Thanks for using fastapi mail, keep using it..!!!</p>


            </body>
            </html>
            """
    validation = validate_email(receiver_email)
    validated_email = validation["email"]
    message = MessageSchema(
        subject=subject,
        body=template,
        recipients=[validated_email],
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(message)


    return True