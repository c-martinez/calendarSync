from datetime import date, time, datetime, timedelta

def startOfToday():
    return datetime.combine(date.today(), time())
    # return datetime(2020, 8, 1, 0, 0)

def getStartDate(deltaT=timedelta(days=30)):
    return (startOfToday() - deltaT)
    # return startOfToday()

def getEndDate(deltaT=timedelta(days=30)):
    return (startOfToday() + deltaT)
