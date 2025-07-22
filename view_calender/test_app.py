import streamlit as st
import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

st.title("Google Calendar Authentication for Streamlit")
if st.button("Authenticate with Google"):
    creds = authenticate_google()
    st.success("Authenticated Successfully!")

    # Example: Fetch Upcoming Calendar Events
    service = build('calendar', 'v3', credentials=creds)
    events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        st.write("No upcoming events found.")
    else:
        st.write("Upcoming events:")
        for event in events:
            st.write(event['summary'], " - ", event['start'].get('dateTime', event['start'].get('date')))
