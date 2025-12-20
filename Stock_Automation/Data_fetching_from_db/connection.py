# file that holds the credential and all the details that contains access points to the db

import firebase_admin
from firebase_admin import credentials , firestore

Credentails = credentials.Certificate('D:/PROJECTS/AGENT-BE/the-chat-44e8e-firebase-adminsdk-fbsvc-7f501ef3f6.json')

app = firebase_admin.initialize_app(Credentails)

db = firestore.client()