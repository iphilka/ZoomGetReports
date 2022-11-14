import datetime
import os
from dotenv import load_dotenv

from ZoomReports import Zoom


load_dotenv()

zoom = Zoom(account_id=os.getenv("ACCOUNT_ID"),
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"))

zoom.get_auth_token()

# meetings = zoom.get_meeting_on_date(datetime.datetime.now(), user_email="ksenia.andreeva@hexlet.io")

meetings = zoom.get_past_meetings(meeting_id="83050322455")

print("Done!")
