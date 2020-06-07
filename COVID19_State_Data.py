#State Cases - Telangana

import requests
from datetime import datetime
import Slack_Push_Notification as Slack
from prettytable import PrettyTable

#This is the API End point where the web-page gets the data from JavaScript Code.
site = 'https://covid19.telangana.gov.in/wp-json/acf/v3/options/covid19-cases'
r = requests.get(site)

#This Dictionary stores the data of all the dates till now as
d = r.json()

#The last record is the Current Record
today = d['acf']['data'][-1]
date = datetime.fromtimestamp(today['date']).strftime('%d-%B-%Y, %H:%M IST (GMT+5:30)')

#Extracting the information from the dictionary - Today's Information
total = today.get('total', None)
active = today['active']
recovered = today.get('recovered', None)
deaths = today.get('deaths', None)

#Adding data to the summary table
state_summ = PrettyTable(['Total', 'Active', 'Recovered', 'Deaths'])
state_summ.add_row([total, active, recovered, deaths])

print(f'******************** TELANGANA CASES (as on {date}) ********************')
print(state_summ)

#Sending SLACK Notification
msg = f"***** TELANGANA Cases ******\nDate: {date}\nTotal: {total}\nActive: {active}\nDeaths: {deaths}"
Slack.slack_message(msg, __file__)

