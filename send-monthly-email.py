from app.GravityForms import GravityForms
import os
from app.email_ses import send_email
from datetime import datetime, date, timedelta


def lambda_handler(event, context):
    html_file = f"{os.environ['LAMBDA_TASK_ROOT']}/app/gcp-automated-process.html"
    last_day_prev_mth = date.today().replace(day=1) - timedelta(days=1)
    first_day_prev_mth = date.today().replace(day=1) - timedelta(days=last_day_prev_mth.day)
    dates = [first_day_prev_mth, last_day_prev_mth]
    id = 6
    gf = GravityForms(secret=os.environ['grav_secret'], key=os.environ['grav_key'])
    gf.write_form_entires_to_file(filename='/tmp/data.csv', form_id=id, date=dates)
    #
    text = "Monthly files are attached."
    html = open(html_file).read()
    sender = "info@givingclosetproject.org"
    to =[
    ]
    message = {"to": to, "from": sender, "subject": "GCP Monthly File",
               "attachments": ["/tmp/Duval_County.csv", "/tmp/Palm_Beach_County.csv"], "text": text, "html": html}
    send_email(message)