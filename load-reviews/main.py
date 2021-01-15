from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import telegram
from shared import bot
import time
import textwrap

# TODO Handle review updates, requires persisting the message (and rating) too

REVIEW_ID = "reviewId"
REVIEW_TEXT = "text"
REVIEW_RATING = "starRating"
REVIEW_LAST_MODIFIED = "lastModified"

play_dev_creds = service_account.Credentials.from_service_account_file(
    "credentials-play-dev.json",
    scopes=["https://www.googleapis.com/auth/androidpublisher"],
)
firestore_creds = credentials.Certificate("credentials-firestore.json")


def on_send_review(event, context):
    print(
        f"This Function was triggered by messageId {context.event_id} published at {context.timestamp}"
    )
    _on_send_review()


def _on_send_review():
    reviews = None
    with build("androidpublisher", "v3", credentials=play_dev_creds) as service:
        try:
            reviews = get_reviews(service)
        except HttpError as e:
            print(
                f"Error response status code : {e.resp.status}, reason : {e.error_details}"
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


review_notifier_send = None


def bot_send_review(review):
    global review_notifier_send

    userComment = next(
        comment for comment in review["comments"] if "userComment" in comment
    )["userComment"]
    rating = userComment[REVIEW_RATING]
    text = userComment[REVIEW_TEXT]
    message = f"""\
    {rating * '★'}{(5 - rating) * '☆'}

    "{text}"
    """

    if not review_notifier_send:
        config = bot.read_config("secrets.json")
        review_notifier_bot = telegram.Bot(token=config.token)
        review_notifier_send = lambda message: bot.send_message(
            review_notifier_bot, config.chat_id, message
        )
    review_notifier_send(textwrap.dedent(message))


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
