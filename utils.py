from datetime import date, time, datetime, timedelta

def startOfToday():
    return datetime.combine(date.today(), time())

def getStartDate():
    # return "2017-04-03"
    return (startOfToday() - timedelta(days=30))

def getEndDate():
    # return "2017-04-04"
    return (startOfToday() + timedelta(days=30))
