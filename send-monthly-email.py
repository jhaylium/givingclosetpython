from app.GravityForms import GravityForms
import os
import re
from app.email_ses import send_email
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()


last_day_prev_mth = date.today().replace(day=1) - timedelta(days=1)
first_day_prev_mth = date.today().replace(day=1) - timedelta(days=last_day_prev_mth.day)
dates = [first_day_prev_mth, last_day_prev_mth]


areas_served = [16, 23]
today = datetime.today().strftime('%Y-%m-%d')
yrmth = f'_{last_day_prev_mth.strftime("%Y_%m")}'
attachments = []
for id in areas_served:
    id
    print(id, filepath)
    gf = GravityForms(secret=os.environ['secret'], key=os.environ['key'])
    form_info = gf.get_form_info(id)
    form_name = re.sub('[^a-zA-Z0-9 \n\.]', '_', form_info['title']).replace(' ', '_')
    form_name = form_name.replace('___', '_')
    print(form_name)
    filepath = f'tmp/{form_name}{yrmth}.csv'
    print(filepath)
    attachments.append(filepath)
    gf.write_form_entires_to_file(filename=filepath, form_id=id,form=form_info, date=dates)

text = "Monthly files are attached."
html = open("files\\gcp-automated-process.html").read()
#awshtml = f"{os.environ['LAMBDA_TASK_ROOT']}/app/gcp-automated-process.html"
sender = "info@givingclosetproject.org"
to = [
    ]

message = {"to": to, "from": sender, "subject": "GCP Monthly File",
           "attachments": attachments, "text": text, "html": html}
send_email(message)