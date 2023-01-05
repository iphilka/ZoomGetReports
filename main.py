import datetime
import pprint
from datetime import date
import os
from dotenv import load_dotenv
import pandas as pd

from ZoomReports import Zoom
from conf import conferences


load_dotenv()

zoom = Zoom(account_id=os.getenv("ACCOUNT_ID"),
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"))

# Авторизуемся
zoom.get_auth_token()

# Определяем дату
date_object = datetime.date.today()
date_str = date_object.strftime("%Y-%m-%d")

# Перебираем все конфернеции из файла
for conference in conferences:
    # TODO: заменить на datetime.date.today()
    meetings = zoom.get_past_meetings(meeting_id=conference.get("meeting_id"), need_date=date_object)
    # Название предмета и группа(?)
    object_name = conference.get("object")
    print(object_name)
    pprint.pprint(meetings)
    # Скипаем если нет конференции
    if not len(meetings) == 0:
        # Получаем отчет об участниках
        participants_report = zoom.get_report_participant_on_meeting(meetings[0])
        df = pd.DataFrame(participants_report.get("participants")).T
        # Транспонируем фрейм
        df = df.transpose()
        # Пересчитываем продолжительность присутствия в минуты
        df["duration"] = df["duration"]/3600

        meeting_date = participants_report.get("meeting_date")
        # Формируем файл
        df.to_excel(excel_writer=f"./files/{object_name}_{meeting_date}.xlsx")

print("Done!")


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', os.getenv("SCOPES"))
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', os.getenv("SCOPES"))
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')

    print('Files:')
    for item in items:
        pprint.pprint(item)
        # print(u'{0} ({1})'.format(item['name'], item['id']))
except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f'An error occurred: {error}')


file_names = os.listdir("./files/")

folder_metadata = {
    'name': date_str,
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': ["1RDPJDx_zFHvpzl3E3PQcHtvY5plWaUV9"]
}
r = service.files().create(body=folder_metadata, fields='id').execute()

for name in file_names:
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'parents': [r["id"]]
        }
    media = MediaFileUpload(f'./files/{name}',
                            mimetype='*/*',
                            resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('File ID: ' + file.get('id'))
    os.remove(f'./files/{name}')
