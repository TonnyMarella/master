import os
import re
import requests
import pandas as pd

from datetime import datetime
from redminelib import Redmine
from dotenv import load_dotenv

load_dotenv()

PRIVATE_TOKEN = os.getenv('PRIVATE_TOKEN')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

id_project = input('Виберіть проект\n1. back\n2. front\n')
projects = {
    '1': '148',
    '2': '147'
}
name_branch = input('Введіть назву гілки(наприклад dev):')
time_from = datetime.strptime(input('Введіть дату з якої буде пошук(формат рік-місяць-день): '), '%Y-%m-%d')
time_to = datetime.strptime(input('Введіть дату до якої буде пошук(формат рік-місяць-день): '), '%Y-%m-%d')

url = "https://gitlab.chmsoft.com.ua/api/v4/projects/" + projects[id_project] + "/merge_requests"

query = {
    'private_token': PRIVATE_TOKEN,
    'per_page': '999',
}

response = requests.get(url, params=query)
merge_requests_list = response.json()

redmine = Redmine('https://redmine.chmsoft.com.ua/', username=EMAIL, password=PASSWORD)
project = redmine.project.get('resto-cloud')
issues = project.issues
result_redmine = {}

for i in issues:
    result_redmine[str(i.id)] = [
        i.description,
        i.status,
        i.assigned_to if 'assigned_to' in dir(i) else ' '
    ]

field_names = ['title', 'number_merge', 'merged_at', 'description', 'id_redmine', 'status_redmine',
               'assigned_to_redmine', 'description_redmine']
result_merge = []

for merge_request in merge_requests_list:
    if merge_request['target_branch'] == name_branch and merge_request['state'] == 'merged':
        time_merge = merge_request['merged_at'][0:10]
        time_merge = datetime.strptime(time_merge, '%Y-%m-%d')
        if time_from <= time_merge <= time_to:
            title_merge = re.sub('\D', '', merge_request['title'][0:6])
            result_merge.append({
                'title': title_merge,
                'number_merge': merge_request['iid'],
                'merged_at': merge_request['merged_at'][0:10] + ' ' + merge_request['merged_at'][11:-1],
                'description': merge_request['description'],
            })

            if title_merge in result_redmine:
                result_merge[-1]['id_redmine'] = title_merge
                result_merge[-1]['status_redmine'] = result_redmine[title_merge][1]
                result_merge[-1]['assigned_to_redmine'] = result_redmine[title_merge][2]
                result_merge[-1]['description_redmine'] = result_redmine[title_merge][0]


sorted_merges = sorted(result_merge, key=lambda d: d['merged_at'])

df = pd.DataFrame(data=sorted_merges)
df.to_excel('merged.xlsx', index=False)
