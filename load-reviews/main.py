from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import telegram
from telegram.error import TelegramError
import time
import json
import textwrap

# TODO Handle review updates, requires persisting the message (and rating) too

REVIEW_ID = "reviewId"
REVIEW_NAME = "authorName"
REVIEW_TEXT = "text"
REVIEW_RATING = "starRating"
REVIEW_LAST_MODIFIED = "lastModified"

play_dev_creds = service_account.Credentials.from_service_account_file(
    "credentials-play-dev.json",
    scopes=["https://www.googleapis.com/auth/androidpublisher"],
)
firestore_creds = credentials.Certificate("credentials-firestore.json")

# TODO Should handle "tokenPagination"
def get_reviews(service):
    """https://developers.google.com/android-publisher/api-ref/rest/v3/reviews/list#http-request"""
    response = (
        service.reviews()
        .list(packageName="com.happy_devs.sudoku", translationLanguage="en")
        .execute()
    )
    if "reviews" in response:
        return response["reviews"]
    else:
        return []


def is_unprocessed(review, processed, processed_ids):
    userComment = next(
        comment for comment in review["comments"] if "userComment" in comment
    )["userComment"]
    index = -1
    try:
        index = processed_ids.index(review[REVIEW_ID])
    except ValueError:
        pass
    return (
        index == -1
        or userComment[REVIEW_LAST_MODIFIED]["seconds"]
        != processed[index][REVIEW_LAST_MODIFIED]["seconds"]
    )


def get_unprocessed_reviews(db, reviews):
    review_ids = [review[REVIEW_ID] for review in reviews]
    processed = db.collection("reviews").where("reviewId", "in", review_ids).get()
    processed = [document_snapshot.to_dict() for document_snapshot in processed]
    processed_ids = [review[REVIEW_ID] for review in processed]
    return [
        review for review in reviews if is_unprocessed(review, processed, processed_ids)
    ]


def bot_send_review(review):
    userComment = next(
        comment for comment in review["comments"] if "userComment" in comment
    )["userComment"]
    authorName = review[REVIEW_NAME] if "authorName" in review else ""
    rating = userComment[REVIEW_RATING]
    text = userComment[REVIEW_TEXT]
    message = f"""\
    {authorName} {rating * '★'}{(5 - rating) * '☆'}

    "{text}"
    """
    bot_send_message(textwrap.dedent(message))


def persistence_representation(review):
    userComment = next(
        comment for comment in review["comments"] if "userComment" in comment
    )["userComment"]
    return {
        REVIEW_ID: review[REVIEW_ID],
        REVIEW_RATING: userComment[REVIEW_RATING],
        REVIEW_TEXT: userComment[REVIEW_TEXT],
        REVIEW_LAST_MODIFIED: userComment[REVIEW_LAST_MODIFIED],
        "added": time.time(),
    }


# FIXME Refactor into reusable module
def bot_send_message(message):
    with open("secrets.json") as f:
        secrets = json.load(f)
        try:
            bot = telegram.Bot(token=secrets["TELEGRAM_TOKEN"])
            bot.sendMessage(chat_id=secrets["TELEGRAM_CHAT_ID"], text=message)
        except TelegramError as e:
            print(f"Failed to send Telegram message { e }")


reviews = None
with build("androidpublisher", "v3", credentials=play_dev_creds) as service:
    try:
        reviews = get_reviews(service)
    except HttpError as e:
        print(
            "Error response status code : {0}, reason : {1}".format(
                e.resp.status, e.error_details
            )
        )
if reviews:
    firebase_admin.initialize_app(firestore_creds)
    db = firestore.client()
    reviews = get_unprocessed_reviews(db, reviews)
    batch = db.batch()
    for review in reviews:
        bot_send_review(review)
        ref = db.collection("reviews").document(review[REVIEW_ID])
        batch.set(ref, persistence_representation(review))
    batch.commit()
