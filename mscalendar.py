import requests

def getCalendarEvents(startDate, endDate):
    startDateStr = startDate.strftime("%Y-%m-%d")
    endDateStr = endDate.strftime("%Y-%m-%d")

    # Generate these automatically
    outlookId = '8b976e423ac54e8fb66046fec5ca86e3@esciencecenter.nl/8d87fbfb7149421d9225c8d5780691fc4828726684233662815'
    url = 'https://outlook.office365.com/owa/calendar/%s/service.svc?action=FindItem&ID=-1&AC=1'%outlookId

    bodyTemplate = open('bodyTemplate.txt', 'r').read()
    body = bodyTemplate%(startDateStr, endDateStr)
    headers = { 'Action': 'FindItem', "Content-Type": "application/json; charset=UTF-8" }

    resp = requests.post(url, headers=headers, data=body)
    respJson = resp.json()

    # Name the things in between just for fun ?
    events = respJson['Body']['ResponseMessages']['Items'][0]['RootFolder']['Items']

    calData = []
    for event in events:
        calEvent = {
            'id'        : event['ItemId']['Id'],
            'start'     : event['Start'],
            'end'       : event['End'],
            'title'     : event['Subject']
        }
        calData.append(calEvent)

    return calData
