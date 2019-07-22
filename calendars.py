from utils import getStartDate, getEndDate
from gcalendar import getCalendarEvents as getGEvents
from gcalendar import insertCalendarEvent, deleteCalendarEvent
from mscalendar import getCalendarEvents as getMSEvents
from dateutil.parser import parse as dateparse

try:
    from ConfigParser import SafeConfigParser
except:
    from configparser import SafeConfigParser

config = SafeConfigParser()
config_filename = 'config.ini'
config.read(config_filename)

BUFFER_CALENDAR_ID = config.get('default', 'BUFFER_CALENDAR_ID')   # TMP CALENDAR
SYNC_CALENDAR_ID = config.get('default', 'SYNC_CALENDAR_ID') # ESCIENCE CALENDAR

print(BUFFER_CALENDAR_ID)

def getGoogleEvents(fromDate, toDate):
    # TODO: Change calendar ID ?
    # Calendar ID
    events = getGEvents(BUFFER_CALENDAR_ID, fromDate, toDate)
    events += getGEvents(SYNC_CALENDAR_ID, fromDate, toDate)
    return events

def getOutlookEvents(fromDate, toDate):
    return getMSEvents(fromDate, toDate)

def normalizeOEvent(event):
    return {
        'id': '???',
        'title': event['title'],
        'start': event['start'],
        'end': event['end'],
    }

def getDateTime(eventTime):
    try:
        return eventTime['dateTime']
    except:
        # Whole day events have only date, not dateTime
        return eventTime['date']

def normalizeGEvent(event):
    return {
        'id': event['id'],
        'title': event['summary'],
        'start': getDateTime(event['start']),
        'end': getDateTime(event['end']),
    }

def printEvents(title, events):
    print(title + ':')
    for event in events:
        print(event['start'] + ': ' + event['title'])
    print('===================================================================')


def getEventHash(event):
    start = dateparse(event['start']).astimezone().isoformat()
    return start + ': ' + event['title']

def getNonOverlapingEvents(sourceEvents, targetEvents, debug=False):
    newEvents = []
    existingEventNames = [ getEventHash(e) for e in sourceEvents ]
    newEvents = [ e for e in targetEvents if getEventHash(e) not in existingEventNames ]
    if debug:
        for i in range(10): print('')
        printEvents('',sourceEvents)
        print('existingEventsNames')
        for e in existingEventNames:
            print('   ',e)
        print('TargetEventTitles:')
        for e in targetEvents:
            print('   ',getEventHash(e))

    return newEvents

def syncCalendars():
    fromDate = getStartDate()
    toDate = getEndDate()

    # fetch outlook calendar as list of events: oEvents
    oEvents = getOutlookEvents(fromDate, toDate)
    oEvents = [ normalizeOEvent(e) for e in oEvents ]
    printEvents('oEvents', oEvents)

    # fetch google calendar as list of events : gEvents
    gEvents = getGoogleEvents(fromDate, toDate)
    gEvents = [ normalizeGEvent(e) for e in gEvents ]
    printEvents('gEvents', gEvents)

    # Check all events on oEvents are in gEvents
    #   rather check events on oEvents which are not in gEvents
    #   and save them as newEvents
    newEvents = getNonOverlapingEvents(gEvents, oEvents, debug=False)
    printEvents('newEvents', newEvents)

    # Check all events on gEvents are still in oEvents (remove cancelations)
    delEvents = getNonOverlapingEvents(oEvents, gEvents)
    printEvents('delEvents', delEvents)

    # Add newEvents to google calendar
    for e in newEvents:
        insertCalendarEvent(BUFFER_CALENDAR_ID, e['title'], e['start'], e['end'])
        pass

    # Remove delEvents from google calendar
    for e in delEvents:
        try:
            deleteCalendarEvent(BUFFER_CALENDAR_ID, e['id'])
            pass
        except:
            print('Cannot deleve event: ' + e['start'] + ': ' + e['title'])

if __name__ == '__main__':
    syncCalendars()
