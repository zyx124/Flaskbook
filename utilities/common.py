import time
import boto3
from flask import current_app

def utc_now_ts():
    return int(time.time())


def email(to_email, subject, body_html, body_text):
    # in the test, do not sent the email
    if current_app.config.get("TESTING"):
        return False

    client = boto3.client('ses')
    return client.send_email(
        Source='zhaoyuxin124@gmail.com',
            Destination={
                'ToAddresses': [
                    to_email,
                ]
            },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body_text,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': body_html,
                    'Charset': 'UTF-8'
                },
            }
        }
    )