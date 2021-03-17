#State Cases - Telangana
import os
import requests
import csv
from datetime import datetime
import Slack_Push_Notification as Slack
from prettytable import PrettyTable



#CSV File Name and Path
#os.chdir('C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python38-32')
filename = 'COVID-19_Telangana_Data.csv'

#This is the API End point where the web-page gets the data from JavaScript Code.
site = 'https://covid19.telangana.gov.in/wp-json/acf/v3/options/covid19-cases'
r = requests.get(site)

#This Dictionary stores the data of all the dates till now as
d = r.json()

#Heading of the CSV file
head = ['DATE', 'TOTAL_CASES', 'ACTIVE_CASES', 'RECOVERED', 'DEATHS']

#Writing the Header to the file
with open(filename, 'w') as f:
    writer = csv.writer(f, delimiter= ',', lineterminator= '\n')
    writer.writerow([x for x in head])


#The last record is the Current Record
today = d['acf']['data'][-1]
date = datetime.fromtimestamp(today['date']).strftime('%d-%B-%Y, %H:%M IST (GMT+5:30)')

#Writing the data to the file
with open(filename, 'a') as f:
    writer = csv.writer(f, delimiter=',', lineterminator='\n')
    for i in d['acf']['data']:
        day = datetime.fromtimestamp(i['date']).strftime('%d-%B-%Y')
        writer.writerow([day, i['total'], i['active'], i['recovered'], i['deaths']])


#Extracting the information from the dictionary - Today's Information
total = today.get('total', None)
active = today['active']
recovered = today.get('recovered', None)
deaths = today.get('deaths', None)

#Adding data to the summary table
state_summ = PrettyTable(['Total', 'Active', 'Recovered', 'Deaths'])
state_summ.add_row([total, active, recovered, deaths])

heading = f' TELANGANA CASES (as on {date}) '.center(120, '*')
print(heading)
print(state_summ)

#Sending SLACK Notification
msg = f"***** TELANGANA Cases ******\nDate: {date}\nTotal: {total}\nActive: {active}\nDeaths: {deaths}"
Slack.slack_message(msg, __file__)
