from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'mail.privateemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'contact@waypointsandwonders.com'
app.config['MAIL_PASSWORD'] = 'ropfy6-sapmyq-bujJer'
app.config['MAIL_DEFAULT_SENDER'] = 'contact@waypointsandwonders.com'
app.config['MAIL_DEBUG'] = True  # Enable debugging

mail = Mail(app)

with app.app_context():
    try:
        msg = Message("Test Email",
                      sender="contact@waypointsandwonders.com",
                      recipients=["harveychaney@gmail.com"],
                      body="This is a test email from Flask-Mail.")
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print("Error:", e)
