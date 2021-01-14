from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

SCOPES = ["https://www.googleapis.com/auth/androidpublisher"]
SERVICE_ACCOUNT_FILE = "credentials.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

with build("androidpublisher", "v3", credentials=credentials) as service:
    try:
        request = service.reviews().list(packageName="com.happy_devs.sudoku")
        # https://developers.google.com/android-publisher/api-ref/rest/v3/reviews/list#http-request
        response = request.execute()
    except HttpError as e:
        print(
            "Error response status code : {0}, reason : {1}".format(
                e.resp.status, e.error_details
            )
        )
