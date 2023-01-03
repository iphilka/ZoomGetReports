from datetime import date
import os
from dotenv import load_dotenv
import pandas as pd

from ZoomReports import Zoom


load_dotenv()

zoom = Zoom(account_id=os.getenv("ACCOUNT_ID"),
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"))

zoom.get_auth_token()

# meetings = zoom.get_meeting_on_date(datetime.datetime.now(), user_email="ksenia.andreeva@hexlet.io")

meetings = zoom.get_past_meetings(meeting_id="86344008075", need_date=date.fromisoformat("2022-09-05"))

participants_report = zoom.get_report_participant_on_meeting(meetings[0])

df = pd.DataFrame(participants_report.get("participants")).T
meeting_date = participants_report.get("meeting_date").split("T")[0]
df.to_excel(excel_writer=f"./files/{meeting_date}.xlsx")

print("Done!")
