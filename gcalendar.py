import pickle

from os import path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events'
    ]

def getService():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def getCalendarEvents(calendarId, startDate, endDate):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    service = getService()

    # Call the Calendar API
    startDateStr = startDate.isoformat() + 'Z' # 'Z' indicates UTC time
    endDateStr = endDate.isoformat() + 'Z' # 'Z' indicates UTC time

    events_result = service.events().list(calendarId=calendarId, timeMin=startDateStr,
                                        timeMax=endDateStr,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def insertCalendarEvent(calendarId, title, startDate, endDate):
    event = {
        'summary': title,
        'description': title + '\nImported event.',
        'start': {
            'dateTime': startDate,
        },
        'end': {
            'dateTime': endDate,
        }
    }

    service = getService()
    event = service.events().insert(calendarId=calendarId, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def deleteCalendarEvent(calendarId, eventId):
    service = getService()
    service.events().delete(calendarId=calendarId, eventId=eventId).execute()
