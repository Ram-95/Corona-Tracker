'''Using the COVID-19 India API - https://api.covid19india.org/v3/min/data.min.json and fetching the required Data.'''

import bs4 as bs
import requests
import json
from prettytable import PrettyTable
import Slack_Push_Notification as Slack

#COVID-19 API - Has all India's Data
url = "https://api.covid19india.org/v3/min/data.min.json"

r = requests.get(url).text

#This Dictionary stores the data of all the dates till now as
d = json.loads(r)

#District Summary Table
head = ['District', 'Total', 'Active', 'Recovered', 'Deceased']
dist_table = PrettyTable(head)

state = 'TG'
state_data = d[state]
#State Timestamp - Denotes the time of Updation
state_ts = state_data['meta']['last_updated'].split('T')[0] + ' ' + state_data['meta']['last_updated'].split('T')[1][:5] + ' IST'


country_data = d['TT']
#Country's Timestamp - Denotes the time of Updation of Data
country_ts = country_data['meta']['last_updated'].split('T')[0] + ' ' + country_data['meta']['last_updated'].split('T')[1][:5] + ' IST'

summ_head = ['Total', 'Active', 'Recovered', 'Deaths', 'Testing Done']
summ_table = PrettyTable(summ_head)

'''Extracting District wise Data of a State'''
for i in d.get(state, 'Not Found').get('districts', 'Not Found'):
    for j in d[state]['districts'][i]['total']:
        confirmed = int(d[state]['districts'][i]['total'].get('confirmed', 0))
        recovered = int(d[state]['districts'][i]['total'].get('recovered', 0))
        deceased = int(d[state]['districts'][i]['total'].get('deceased', 0))

        active = confirmed - (recovered + deceased)
        
    #Adding the data to the Table
    dist_table.add_row([i, confirmed, active, recovered, deceased])

'''Extracting State's Data.'''
confirmed = str(state_data['total'].get('confirmed', 0)) + '(+' + str(state_data['delta'].get('confirmed', 0)) + ')'
recovered = str(state_data['total'].get('recovered', 0)) + '(+' + str(state_data['delta'].get('recovered', 0)) + ')'
deceased = str(state_data['total'].get('deceased', 0)) +  '(+' + str(state_data['delta'].get('deceased', 0)) + ')'
tested = state_data['total'].get('tested', 0)
active = state_data['total'].get('confirmed', 0) - (state_data['total'].get('recovered', 0) + state_data['total'].get('deceased', 0))

summ_table.add_row([confirmed, active, recovered, deceased, tested])
print(f'\nDistrict-wise cases across the state\n{dist_table}')
print(f'\nState Summary as on {state_ts}:\n{summ_table}')

#Sending SLACK Notification - State's Data
state_msg = f"***** TELANGANA Cases ******\nDate: {state_ts}\nTotal: {confirmed}\nActive: {active}\nRecovered: {recovered}\nTests Done: {tested}\nDeaths: {deceased}"
Slack.slack_message(state_msg, __file__)


'''Extracting India Data.'''
ind_table = PrettyTable(summ_head)

confirmed = str(country_data['total'].get('confirmed', 0)) + '(+' + str(country_data['delta'].get('confirmed', 0)) + ')'
recovered = str(country_data['total'].get('recovered', 0)) + '(+' + str(country_data['delta'].get('recovered', 0)) + ')'
deceased = str(country_data['total'].get('deceased', 0)) +  '(+' + str(country_data['delta'].get('deceased', 0)) + ')'
tested = str(country_data['total'].get('tested', 0)) + '(+' + str(country_data['delta'].get('tested', 0)) + ')'
active = country_data['total'].get('confirmed', 0) - (country_data['total'].get('recovered', 0) + country_data['total'].get('deceased', 0))

ind_table.add_row([confirmed, active, recovered, deceased, tested])
print(f'\nIndia Cases Summary as on {country_ts}:\n{ind_table}')


#Sending SLACK Notification - Country's Data
india_msg = f"***** INDIA Cases ******\nDate: {country_ts}\nTotal: {confirmed}\nActive: {active}\nRecovered: {recovered}\nTests Done: {tested}\nDeaths: {deceased}"
Slack.slack_message(india_msg, __file__)

