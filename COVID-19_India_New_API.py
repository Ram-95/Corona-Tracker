'''Using the COVID-19 India API - https://api.covid19india.org/v3/min/data.min.json and fetching the required Data.'''
import os
import bs4 as bs
import csv
import requests
import json
from prettytable import PrettyTable
import Slack_Push_Notification as Slack

#COVID-19 API - Has all India's Data
url = "https://api.covid19india.org/v3/min/data.min.json"
r = requests.get(url).text

#This Dictionary stores the data of all the dates till now as
d = json.loads(r)

#Dictionary to store the State Codes(Used in the API) and State Names
#UN - UnAssigned and TT - Total India Cases are NOT present in this dictionary
state_code = {'AN': 'Andaman and Nicobar', 'AP': 'Andhra Pradesh', 'AR': 'Arunachal Pradesh', 'AS': 'Assam', 'BR': 'Bihar',
              'CH': 'Chandigarh', 'CT': 'Chattisgarh', 'DL': 'Delhi', 'DN': 'Dadra and Nagar Haveli', 'GA': 'Goa', 'GJ': 'Gujarat',
              'HP': 'Himachal Pradesh', 'HR': 'Haryana', 'JH': 'Jharkhand', 'JK': 'Jammu and Kashmir', 'KA': 'Karnataka', 'KL': 'Kerala',
              'LA': 'Ladakh', 'LD': 'Lakshadweep', 'MH': 'Maharashtra', 'ML': 'Meghalaya', 'MN': 'Manipur', 'MP': 'Madhya Pradesh',
              'MZ': 'Mizoram', 'NL': 'Nagaland', 'OR': 'Odisha', 'PB': 'Punjab', 'PY': 'Puducherry', 'RJ': 'Rajasthan', 'SK': 'Sikkim',
              'TG': 'Telangana', 'TN': 'Tamil Nadu', 'TR': 'Tripura', 'UP': 'Uttar Pradesh', 'UT': 'Uttarakhand', 'WB': 'West Bengal'}


def getIndiaData():
    '''Prints the statewise details of Corona Cases.'''
    head = ['State/UT', 'Total', 'Active', 'Recovered', 'Deceased', 'Tests Done']
    ind_state_table = PrettyTable(head)

    for i in state_code:
        if 'total' in d[i]:
            confirmed = d[i]['total'].get('confirmed', 0)
            deceased = d[i]['total'].get('deceased', 0)
            recovered = d[i]['total'].get('recovered', 0)
            tested = d[i]['total'].get('tested', 0)

            active = confirmed - (deceased + recovered)

            ind_state_table.add_row([state_code[i], confirmed, active, recovered, deceased, tested])
        else:
            continue
    

    print(f'{ind_state_table}')


def getStateData(state):
    '''Prints the District Level Data of a given State, State Summary and India Summary of Corona Cases.'''
    #try:
    #District Summary Table
    head = ['District', 'Total', 'Active', 'Recovered', 'Deceased']
    dist_table = PrettyTable(head)

    try:
        state_data = d[state]
    except:
        print(f'No State Found with this Code')

    #CSV Filename and Path
    os.chdir('C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python38\\Corona-Tracker\\')
    dist_filename = f'COVID-19_{state_code[state]}_Districts_Data.csv'

    #Writing the Header to the file
    with open(dist_filename, 'w') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        writer.writerow([x.upper() for x in head])

    #State Timestamp - Denotes the time of Updation
    state_ts = state_data['meta']['last_updated'].split('T')[0] + ' ' + state_data['meta']['last_updated'].split('T')[1][:5] + ' IST'


    country_data = d['TT']
    #Country's Timestamp - Denotes the time of Updation of Data
    country_ts = country_data['meta']['last_updated'].split('T')[0] + ' ' + country_data['meta']['last_updated'].split('T')[1][:5] + ' IST'

    summ_head = ['Total', 'Active', 'Recovered', 'Deaths', 'Testing Done']
    summ_table = PrettyTable(summ_head)

    '''Extracting District wise Data of a State'''
    with open(dist_filename, 'a') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        for i in d.get(state, 'Not Found').get('districts', 'Not Found'):
            for j in d[state]['districts'][i]['total']:
                confirmed = int(d[state]['districts'][i]['total'].get('confirmed', 0))
                recovered = int(d[state]['districts'][i]['total'].get('recovered', 0))
                deceased = int(d[state]['districts'][i]['total'].get('deceased', 0))

                active = confirmed - (recovered + deceased)
            
            #Adding the data to the Table
            dist_table.add_row([i, confirmed, active, recovered, deceased])
            writer.writerow([i, confirmed, active, recovered, deceased])

    print(f'\nFile Created Successfully. <<< {dist_filename} >>>\n')

    '''Extracting State's Data.'''
    confirmed = str(state_data['total'].get('confirmed', 0)) + '(+' + str(state_data['delta'].get('confirmed', 0)) + ')' if 'delta' in state_data else state_data['total'].get('confirmed', 0)
    recovered = str(state_data['total'].get('recovered', 0)) + '(+' + str(state_data['delta'].get('recovered', 0)) + ')' if 'delta' in state_data else state_data['total'].get('recovered', 0)
    deceased = str(state_data['total'].get('deceased', 0)) +  '(+' + str(state_data['delta'].get('deceased', 0)) + ')' if 'delta' in state_data else state_data['total'].get('deceased', 0)
    tested = state_data['total'].get('tested', 0)
    active = state_data['total'].get('confirmed', 0) - (state_data['total'].get('recovered', 0) + state_data['total'].get('deceased', 0))

    summ_table.add_row([confirmed, active, recovered, deceased, tested])
    print(f" Cases across {state_code.get(state, 'Unknown')} (District wise details) ".center(60,'*'))
    print(f'{dist_table}\n')
    print(f' {state_code[state].title()} Cases Summary (as on {state_ts})'.center(60,'*'))
    print(f'{summ_table}\n')

    #Sending SLACK Notification - State's Data
    state_msg = f"***** {state_code.get(state, 'Unknown')} Cases ******\nDate: {state_ts}\nTotal: {confirmed}\nActive: {active}\nRecovered: {recovered}\nTests Done: {tested}\nDeaths: {deceased}"
    Slack.slack_message(state_msg, __file__)


    '''Extracting India Data.'''
    ind_table = PrettyTable(summ_head)

    confirmed = str(country_data['total'].get('confirmed', 0)) + '(+' + str(country_data['delta'].get('confirmed', 0)) + ')' if 'delta' in country_data else country_data['total'].get('confirmed', 0)
    recovered = str(country_data['total'].get('recovered', 0)) + '(+' + str(country_data['delta'].get('recovered', 0)) + ')' if 'delta' in country_data else country_data['total'].get('recovered', 0)
    deceased = str(country_data['total'].get('deceased', 0)) +  '(+' + str(country_data['delta'].get('deceased', 0)) + ')' if 'delta' in country_data else country_data['total'].get('deceased', 0)
    tested = str(country_data['total'].get('tested', 0)) + '(+' + str(country_data['delta'].get('tested', 0)) + ')'
    active = country_data['total'].get('confirmed', 0) - (country_data['total'].get('recovered', 0) + country_data['total'].get('deceased', 0))

    ind_table.add_row([confirmed, active, recovered, deceased, tested])
    print(f' India Cases Summary (as on {country_ts}) '.center(60,'*'))
    print(f'{ind_table}')


    #Sending SLACK Notification - Country's Data
    india_msg = f"***** INDIA Cases ******\nDate: {country_ts}\nTotal: {confirmed}\nActive: {active}\nRecovered: {recovered}\nTests Done: {tested}\nDeaths: {deceased}"
    Slack.slack_message(india_msg, __file__)
    #except:
        #print(f'EXCEPTION:')


#Driver Code - Pass the State Code as the argument.
getStateData('TG')
