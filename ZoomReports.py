import pprint
from datetime import date, datetime
from base64 import b64encode
import requests
import json

import urllib.parse as parser


class Zoom:
    """ Класс для работы с ZoomAPI"""
    def __init__(self, account_id: str, client_id: str, client_secret: str):
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = "https://zoom.us/oauth/token"
        self.base_url = "https://api.zoom.us/v2"
        self.access_token = ""

    def get_auth_token(self):
        """Получаем токен авторизации ZoomAPI"""

        b_auth_token = b64encode(bytes(f"{self.client_id}:{self.client_secret}", "utf-8"))
        auth_token = b_auth_token.decode('utf-8')

        headers = {
            "Authorization": f"Basic {auth_token}",
        }

        params = {
            "grant_type": "account_credentials",
            "account_id": self.account_id
        }
        response = requests.post(self.auth_url, headers=headers, params=params)
        if response.status_code == 200:
            response = json.loads(response.text)
            self.access_token = response.get("access_token")
        else:
            raise Exception("Запрос не обработан")

    def get_meeting_on_date(self, date: datetime, user_email: str = None) -> list:
        """Получаем список всех конференций на указанную дату для конкретного аккаунта,
        если он не указан, то список всех конференции аккаунта администратора"""
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        # нужна для прохождения пагинации ответа
        page_number = 1

        if user_email:
            meetings_url = f"/users/{user_email}/meetings"
        else:
            meetings_url = "/users/me/meetings"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

        while True:
            params = {
                "type": "previous_meetings",
                "page_number": page_number
            }

            response = requests.get(f"{self.base_url}{meetings_url}", headers=headers, params=params)

            meetings = []

            if response.status_code == 200:
                response = json.loads(response.text)
                meetings_from_response = response.get("meetings")

                for meet in meetings_from_response:
                    # переводим дату из конференции в нужный формат и проверяем соответствие искомой даты
                    # и даты конференции
                    meet_datetime = datetime.strptime(meet.get("start_time"), "%Y-%m-%dT%H:%M:%SZ")
                    meet_date = meet_datetime.replace(hour=0, minute=0, second=0)
                    if date == meet_date:
                        meetings.append(meet)
                    elif date < meet_date:
                        continue
                    else:
                        return meetings

                page_count = response.get("page_count")
                page_number += 1

                if page_count < page_number:
                    break
            else:
                raise Exception("Something wrong!")

        return meetings

    def get_past_meetings(self, meeting_id: str, need_date: date = None) -> list:
        """Получаем список прошедших конференций для переданного ID, если передается дата"""
        past_meetings_url = f"/past_meetings/{meeting_id}/instances"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.get(url=f"{self.base_url}{past_meetings_url}", headers=headers)

        if response.status_code == 200:
            response = json.loads(response.text)
            meetings = response.get("meetings")
            meetings.sort(key=lambda x: x["start_time"], reverse=True)
        else:
            raise Exception("Error from getting past meetings method!")

        if not date:
            return meetings
        else:
            # убираем собрания с ненужной датой
            for meet in list(meetings):
                meet_date = datetime.strptime(meet.get("start_time"), "%Y-%m-%dT%H:%M:%SZ").date()
                if not meet_date == need_date:
                    meetings.remove(meet)
                    print(f"Not equal: meet_date - {meet_date} || need_date - {need_date}")
            pprint.pprint(meetings)
            return meetings

    def get_report_participant_on_meeting(self, meeting: dict) -> dict:
        """Получаем отчет о пользователях по конкретной конференции"""

        # добавить двойной энкодинг для uuid (на случай получения / в uuid)
        meeting_uuid = meeting.get("uuid")
        # meeting_date = datetime.strptime(meeting.get("start_date"), "%Y-%m-%dT%H:%M:%SZ")
        meeting_date = meeting.get("start_time")
        meeting_id = parser.quote(parser.quote(meeting_uuid))
        print(meeting_id)

        report_participant_url = f"{self.base_url}/report/meetings/{meeting_id}/participants"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

        # TODO: предусмотреть вариант, с количеством участников > 300
        params = {
            "page_size": 300,  # хардкожу ответ от api до 300 ответов, чтобы не перебирать страницы
        }

        response = requests.get(url=report_participant_url, headers=headers, params=params)
        if response.status_code == 200:
            response = json.loads(response.text)
            data = {
                "participants": response.get("participants"),
                "meeting_date": meeting_date,
            }
            return data
