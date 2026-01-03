# file that holds the credential and all the details that contains access points to the db
import os
import firebase_admin
from firebase_admin import credentials , firestore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

cred_path = os.path.join(
    BASE_DIR,
    "the-chat-44e8e-firebase-adminsdk-fbsvc-7f501ef3f6.json"
)



Credentails = credentials.Certificate(cred_path)

app = firebase_admin.initialize_app(Credentails)

db = firestore.client()