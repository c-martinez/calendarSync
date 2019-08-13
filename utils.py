from datetime import date, time, datetime, timedelta

def startOfToday():
    return datetime.combine(date.today(), time())

def getStartDate(deltaT=timedelta(days=30)):
    return (startOfToday() - deltaT)

def getEndDate(deltaT=timedelta(days=30)):
    return (startOfToday() + deltaT)
