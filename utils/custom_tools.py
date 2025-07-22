from datetime import datetime, timedelta
import pytz

from langchain.tools import Tool
from faq_retriever import faq_vdb_retriever
from listings_retriever import listings_retriever



def faq_retriever_tool(query: str):
    """This tool is called when user query is about FAQs."""
    retrieved_docs = faq_vdb_retriever.invoke(query)

    if not retrieved_docs:
        return {"documents": [], "metadata": "No relevant documents found."}

    metadata_list = []
    docs_list = []

    for doc in retrieved_docs:
        text = doc.page_content
        source = doc.metadata
        docs_list.append(text)
        metadata_list.append(source)

    return {"documents": docs_list, "metadata": metadata_list}


def listings_retriever_tool(query: str):
    """This is a tool called when user query is about property."""
    retrieved_docs = listings_retriever.invoke(query)

    if not retrieved_docs:
        return {"documents": [], "metadata": "No relevant documents found."}

    metadata_list = []
    docs_list = []

    for doc in retrieved_docs:
        text = doc.page_content
        source = doc.metadata
        docs_list.append(text)
        metadata_list.append(source)

    return {"documents": docs_list, "metadata": metadata_list}


def is_date_available(client_data, service):
    pk_tz = pytz.timezone("America/New_York")

    current_date = datetime.now(pk_tz).date()
    provided_date = datetime.strptime(client_data['date'], "%Y-%m-%d").date()

    if provided_date < current_date:
        print("Provided date is in the past. Please select a future date.")
        return False

    start_time = datetime.combine(provided_date, datetime.strptime("09:00", "%H:%M").time())
    end_time = datetime.combine(provided_date, datetime.strptime("17:00", "%H:%M").time())
    start_time = pk_tz.localize(start_time)
    end_time = pk_tz.localize(end_time)
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    busy_slots = []
    for event in events:
        event_start = datetime.fromisoformat(event['start'].get('dateTime')).astimezone(pk_tz)
        event_end = datetime.fromisoformat(event['end'].get('dateTime')).astimezone(pk_tz)
        busy_slots.append((event_start, event_end))
    current_slot_start = start_time

    while current_slot_start < end_time:
        current_slot_end = current_slot_start + timedelta(hours=1)
        is_free = all(
            current_slot_end <= busy_start or current_slot_start >= busy_end
            for busy_start, busy_end in busy_slots
        )

        if is_free:
            return True
        current_slot_start += timedelta(hours=1)
    return False


def get_meeting_slot(date, service):
    pk_tz = pytz.timezone("America/New_York")

    provided_date = datetime.strptime(date, "%Y-%m-%d").date()

    start_time = datetime.combine(provided_date, datetime.strptime("09:00", "%H:%M").time())
    end_time = datetime.combine(provided_date, datetime.strptime("17:00", "%H:%M").time())

    start_time = pk_tz.localize(start_time)
    end_time = pk_tz.localize(end_time)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    busy_slots = []
    for event in events:
        event_start = datetime.fromisoformat(event['start'].get('dateTime')).astimezone(pk_tz)
        event_end = datetime.fromisoformat(event['end'].get('dateTime')).astimezone(pk_tz)
        busy_slots.append((event_start, event_end))

    current_slot_start = start_time

    while current_slot_start < end_time:
        current_slot_end = current_slot_start + timedelta(hours=1)
        is_free = all(
            current_slot_end <= busy_start or current_slot_start >= busy_end
            for busy_start, busy_end in busy_slots
        )
        if is_free:
            return True, current_slot_start, current_slot_end
        current_slot_start += timedelta(hours=1)
    return False, False, False


def add_meeting_to_calender(client_data, service):
    provided_date = client_data['date']

    meeting_slot = get_meeting_slot(provided_date, service)
    if meeting_slot[0]:
        print("Available slot")
        print(meeting_slot[1], meeting_slot[2])

    start_datetime = datetime.strptime(f"{provided_date}", "%Y-%m-%d")
    end_datetime = start_datetime + timedelta(minutes=30)
    title = f"Meeting for {client_data['name']}"
    event = {
        'title': title,
        'summary': f"This meeting is scheduled for client {client_data['name']} to connect with real-estate agent.",
        'start': {
            'dateTime': meeting_slot[1].isoformat(),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': meeting_slot[2].isoformat(),
            'timeZone': 'America/New_York',
        },
        'attendees': [{'email': client_data['email']}],
        'reminders': {
            'useDefault': True,
        }
    }
    event = service.events().insert(calendarId='primary', body=event).execute()

    def readable_datetime(dt):
        return dt.strftime("%A, %B %d, %Y at %I:%M %p %Z")

    scheduled_slot = readable_datetime(meeting_slot[1])
    return f"Your meeting is scheduled at {scheduled_slot}. Is there anything else I can help you with?"


faq_retriever_tool = Tool(
    name="faq_retriever",
    description="Retrieve FAQ chunks.",
    func=faq_retriever_tool
)

property_listings_retriever_tool = Tool(
    name="listings_retriever",
    description="Retrieve property listings.",
    func=listings_retriever_tool
)

# calendar_availability_checker
datetime_tool = Tool(
    name="current_datetime_retriever",
    func=lambda x: datetime.datetime.now(),
    description="Returns the current date and time",
)

