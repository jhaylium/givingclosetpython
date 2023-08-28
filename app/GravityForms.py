import os
from dotenv import load_dotenv
import datetime
import requests
import logging
import json
import csv

load_dotenv()
#
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

fileHandler = logging.FileHandler(f"gravity_logs_{datetime.datetime.utcnow().strftime('%Y-%m-%d')}.log")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

logger.setLevel(logging.DEBUG)


class GravityForms:

    def __init__(self, secret, key, date=None):
        self.url = "https://givingclosetproject.org/wp-json/gf/v2"
        self.consumer_secret = secret
        self.consumer_key = key
        self.headers = {"Content-Type": "application/json",
                        "User-Agent": "PostmanRuntime/7.28.3"
                        # "User-Agent": "PostmanRuntime/7.28.3"
                        }
        begin_last_week = datetime.datetime.today() - datetime.timedelta(days=datetime.datetime.today().weekday(),
                                                                 weeks=1)
        if date:
            self.report_date = date
        else:
            self.report_date =begin_last_week.strftime('%Y-%m-%d')
        self.today = datetime.datetime.today().strftime('%Y-%m-%d')
        if __name__ == "__main__":
            self.tmp_path = "..\\tmp\\"
        else:
            self.tmp_path = "tmp\\"


    def get_forms(self):
        print(self.consumer_key)
        print(self.consumer_secret)
        r = requests.get(f"{self.url}/forms",
                         headers=self.headers,
                         auth=(self.consumer_key, self.consumer_secret))
        print(r.request.url)
        print(r.request.body)
        print(r.request.headers)
        print(r.status_code)
        if r.status_code == 200:
            return r.json()
        else:
            print(r.content)
            return -1

    def get_form_info(self, form_id):
        r = requests.get(f"{self.url}/forms/{form_id}",
                         headers=self.headers,
                         auth=(self.consumer_key, self.consumer_secret))
        print(r.status_code)
        if r.status_code == 200:
            return r.json()
        else:
            print(r.content)
            return -1

    def get_form_entries(self, form_id, date=None):
        # r = requests.get(f"{self.url}/forms/{form_id}/entries?paging[page_size]=1000",
        #                  auth=(self.consumer_key, self.consumer_secret))
        # date_search ='{"start_date":"2021-11-01", "end_date": "2021-11-30"}'
        if date is None:
            date = self.report_date
            date_search = f'{{"start_date": "{date}"}}'
        elif type(date) == list:
            date_search = f'{{"start_date":"{date[0]}", "end_date": "{date[1]}"}}'
        else:
            date_search = f'{{"start_date": "{date}"}}'
        print(date_search)
        r = requests.get(f"{self.url}/forms/{form_id}/entries?search={date_search}&paging[page_size]=1000",
                         headers=self.headers,
                         auth=(self.consumer_key, self.consumer_secret))
        print(r.status_code)
        if r.status_code == 200:
            return r.json()
        else:
            print(r.content)
            return -1

    def get_all_form_entries(self, form_id):
        # r = requests.get(f"{self.url}/forms/{form_id}/entries?paging[page_size]=1000",
        #                  auth=(self.consumer_key, self.consumer_secret))
        # date_search ='{"start_date":"2021-04-01", "end_date": "2021-04-02"}'
        date_search = f'{{"start_date": "{self.report_date}"}}'
        # date_search = f'{{"start_date": "2021-10-25"}}'
        print(date_search)
        r = requests.get(f"{self.url}/forms/{form_id}/entries?paging[page_size]=1000",
                         headers=self.headers,
                         auth=(self.consumer_key, self.consumer_secret))
        print(r.status_code)
        if r.status_code == 200:
            print(r.json())
            return r.json()
        else:
            print(r.content)
            return -1

    # def write_form_entires_to_file(self, filename, form_id, full=False, date=None, legacy=False):
    def write_form_entires_to_file(self, filename, form, form_id, full=False, date=None, legacy=False):
        print(form)
        # print(f'form id: {form_id}')
        # print(form)
        fields = {}
        for field in form['fields']:
            fields[str(field['id'])] = field['label']
            inputs = field.get('inputs')
            if inputs:
                for input in inputs:
                    fields[input['id']] = input['label']
        fields_to_add = ['date_created', 'ip', 'user_agent', 'id']
        for i in fields_to_add:
            fields[i] = i
        if full:
            data = self.get_all_form_entries(form_id)
        else:
            data = self.get_form_entries(form_id, date)
        print(data)
        json.dumps(data, indent=4)
        list_fields = [str(i) for i in fields.keys()]
        print(list_fields)
        if legacy:
            closet_location= [i['28'] for i in data['entries']]
            closet_locations = set(closet_location)
        master_data = open('tmp\\master-data.json', 'w')
        json.dump(data, master_data)
        with open(filename, 'w') as master_data_file:
            master_writer = csv.DictWriter(master_data_file,
                                           fieldnames=list_fields,
                                           extrasaction='ignore',
                                            delimiter=",",
                                           lineterminator='\n')
            master_writer.writerow(fields)
            if legacy:
                for i in closet_locations:
                    with open(f"{self.tmp_path}{i.replace(' ', '_')}.csv", 'w') as file:
                        writer = csv.DictWriter(file, fieldnames=list_fields, extrasaction='ignore', lineterminator='\n')
                        writer.writerow(fields)
            for i in data['entries']:
                master_writer.writerow(i)
                if legacy:
                    with open(f"tmp\\{i['28'].replace(' ', '_')}.csv", 'a') as data_file:
                        writer = csv.DictWriter(data_file, fieldnames=list_fields, extrasaction='ignore', lineterminator='\n')
                        writer.writerow(i)
            master_data.close()

    def create_file_referrer(self):
        self.delete_ref_files()
        with open("..\\tmp\\master_data.csv", 'r') as file:
            reader = csv.DictReader(file)
            data = [i for i in reader]
            fields = data[0].keys()
            for i in data:
                print(i)
                filename = f"..\\ref-files\\{i['Choose our closest location']}\\{i['First Name'] + ' ' + i['Last Name']}_data.csv"
                # if datetime.datetime.strptime(i['date_created']) >
                if os.path.exists(filename):
                    with open(filename, "a") as data_file:
                        writer = csv.DictWriter(data_file, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
                        writer.writerow(i)
                else:
                    with open(filename, "a") as data_file:
                        writer = csv.DictWriter(data_file, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
                        writer.writeheader()
                        writer.writerow(i)


    def delete_ref_files(self):
        path = f"..\\ref-files\\"
        root = os.listdir(path)
        for i in root:
            directory = f"{path}\\{i}"
            print(directory)
            files = os.listdir(directory)
            if len(files) > 0:
                for i in files:
                    os.remove(f"{directory}\\{i}")


if __name__ == "__main__":
    id = 6
    gf = GravityForms(secret=os.environ['secret'], key=os.environ['key'])
    y = gf.get_forms()
    print(y)
    d = gf.get_form_entries(id)
    x = gf.get_form_info(id)
    print(x['id'])
    # gf.write_form_entires_to_file('../tmp/data.csv', id)
    # gf.create_file_referrer()
    # gf.delete_ref_files()