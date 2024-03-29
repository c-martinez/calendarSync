"""Calendar sync.

Usage:
  calendars.py (--days | --weeks | --months | --years) [--dry-run] [--flush]

Options:
  --days       Sync calendars 7 days before & after today..
  --weeks      Sync calendars 4 weeks before & after today..
  --months     Sync calendars 3 months before & after today.
  --years      Sync calendars one year before & after today.
  --dry-run    Show events to be created / deleted without actually creating them.
  --flush      Instead of sync, removes duplicates in google calendar.
"""
from configparser import ConfigParser
from docopt import docopt
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as dateparse


from utils import getStartDate, getEndDate
from gcalendar import getCalendarEvents as getGEvents
from gcalendar import insertCalendarEvent, deleteCalendarEvent
from mscalendar import getCalendarEvents as getMSEvents


config = ConfigParser()
config_filename = 'config.ini'
config.read(config_filename)

ESCIENCE_CALENDAR_ID = config.get('default', 'ESCIENCE_CALENDAR_ID')   # ESCIENCE CALENDAR

def getOutlookEvents(fromDate, toDate):
    return getMSEvents(fromDate, toDate)

def normalizeOEvent(event):
    return {
        'id': '???',
        'title': event['title'],
        'start': event['start'],
        'end': event['end'],
        'location': event['location']
    }

def normalizeOEvents(events):
    normEvents = []
    for e in events:
        e = normalizeOEvent(e)
        if not e['title'].startswith('Private'):
            normEvents.append(e)
    return normEvents

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

def normalizeGEvents(gEvents):
    return [ normalizeGEvent(e) for e in gEvents ]

def printEvents(title, events):
    print(title + ':')
    for event in events:
        print(event['start'] + ': ' + event['title'])
    print('===================================================================')


def getEventHash(event):
    try:
        startParsed = dateparse(event['start'])
        start = startParsed.astimezone().isoformat()
    except:
        startParsed = dateparse(event['start'] + 'T00:00:00Z')
        start = startParsed.astimezone().isoformat()
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

def deleteDuplicates(deltaT, dryrun=False):
    fromDate = getStartDate(deltaT)
    toDate = getEndDate(deltaT)
    print('Sync period: {startDate:%Y-%m-%d} - {endDate:%Y-%m-%d}'.format(startDate=fromDate, endDate=toDate))

    # fetch google calendar as list of events : gEvents
    gEvents = getGEvents(ESCIENCE_CALENDAR_ID, fromDate, toDate)
    gEvents = normalizeGEvents(gEvents)
    printEvents('gEvents', gEvents)

    uniqueEventHashes = []
    delEvents = []
    for event in gEvents:
        eHash = getEventHash(event)
        if eHash in uniqueEventHashes:
            delEvents.append(event)
        else:
            uniqueEventHashes.append(eHash)

    print('========================================')
    print('===  DELETING EVENTS ==================')
    print('========================================')
    # Remove delEvents from google calendar
    for e in delEvents:
        try:
            print('Deleting event: %s'%getEventHash(e))
            if not dryrun:
                deleteCalendarEvent(ESCIENCE_CALENDAR_ID, e['id'])
        except:
            print('Cannot deleve event: ' + e['start'] + ': ' + e['title'])


def copyToPivotCalendar(deltaT, dryrun=False):
    fromDate = getStartDate(deltaT)
    toDate = getEndDate(deltaT)
    print('Sync period: {startDate:%Y-%m-%d} - {endDate:%Y-%m-%d}'.format(startDate=fromDate, endDate=toDate))

    # fetch outlook calendar as list of events: oEvents
    oEvents = getOutlookEvents(fromDate, toDate)
    oEvents = normalizeOEvents(oEvents)
    # printEvents('oEvents', oEvents)

    # fetch google calendar as list of events : gEvents
    gEvents = getGEvents(ESCIENCE_CALENDAR_ID, fromDate, toDate)
    gEvents = normalizeGEvents(gEvents)
    # printEvents('gEvents', gEvents)

    oEventDict = { getEventHash(e): e for e in oEvents }
    gEventDict = { getEventHash(e): e for e in gEvents }

    oEventSet = set(oEventDict.keys())
    gEventSet = set(gEventDict.keys())

    newEvents = oEventSet - gEventSet
    delEvents = gEventSet - oEventSet

    print('========================================')
    print('===  INSERTING EVENTS ==================')
    print('========================================')
    # Add newEvents to google calendar
    for eKey in newEvents:
        e = oEventDict[eKey]
        print('Creating event: %s'%getEventHash(e))
        if not dryrun:
            insertCalendarEvent(ESCIENCE_CALENDAR_ID, e['title'], e['start'], e['end'], e['location'])

    print('========================================')
    print('===  DELETING EVENTS ==================')
    print('========================================')
    # Remove delEvents from google calendar
    for eKey in delEvents:
        e = gEventDict[eKey]
        try:
            print('Deleting event: %s'%getEventHash(e))
            if not dryrun:
                deleteCalendarEvent(ESCIENCE_CALENDAR_ID, e['id'])
        except:
            print('Cannot deleve event: ' + e['start'] + ': ' + e['title'])


def _buildDeltaT(opts):
    if opts['--days']:
        return timedelta(days=7)
    if opts['--weeks']:
        return timedelta(weeks=4)
    if opts['--months']:
        return relativedelta(months=3)
    if opts['--years']:
        return relativedelta(years=1)

if __name__ == '__main__':
    opts = docopt(__doc__, version='Calendar Sync 1.0')
    deltaT = _buildDeltaT(opts)
    if opts['--flush']:
        deleteDuplicates(dryrun=opts['--dry-run'], deltaT=deltaT)
    else:
        copyToPivotCalendar(dryrun=opts['--dry-run'], deltaT=deltaT)
