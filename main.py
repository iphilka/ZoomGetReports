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

# Перебираем все конфернеции из файла
for conference in conferences:
    # TODO: заменить на datetime.date.today()
    meetings = zoom.get_past_meetings(meeting_id=conference.get("meeting_id"), need_date=date.fromisoformat("2022-12-19"))
    # Название предмета и группа(?)
    object_name = conference.get("object")
    print(object_name)
    pprint.pprint(meetings)
    # Скипаем е сли нет конференции
    if not len(meetings) == 0:
        # Получаем отчет об участниках
        participants_report = zoom.get_report_participant_on_meeting(meetings[0])
        df = pd.DataFrame(participants_report.get("participants")).T
        # Транспонируем флейм
        df = df.transpose()
        # Пересчитываем продолжительность присутствия в минуты
        df["duration"] = df["duration"]/3600

        meeting_date = participants_report.get("meeting_date")
        # Формируем файл
        df.to_excel(excel_writer=f"./files/{object_name}_{meeting_date}.xlsx")

print("Done!")
