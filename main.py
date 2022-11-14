import os
from dotenv import load_dotenv

from ZoomReports import Zoom


load_dotenv()

zoom = Zoom(account_id=os.getenv("ACCOUNT_ID"),
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"))

zoom.get_auth_token()

print("Done!")
