from datetime import datetime, timedelta

def getStartDate():
    # return "2017-04-03"
    return datetime.now()

def getEndDate():
    # return "2017-04-04"
    return (datetime.now() + timedelta(days=30))
