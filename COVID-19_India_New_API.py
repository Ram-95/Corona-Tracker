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

#Slack Notification ON - 1; OFF - 0
slack_notify = 0

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
    '''Prints the statewise details of Corona Cases across India.'''
    head = ['State/UT', 'Total', 'Active', 'Recovered', 'Deceased', 'Tests Done']
    ind_state_table = PrettyTable(head)
    ind_stats = PrettyTable(['Recovery', 'Deaths', 'Affected'])
    summ_head = ['Total', 'Active', 'Recovered', 'Deaths', 'Testing Done']

    country_data = d['TT']
    #Country's Timestamp - Denotes the time of Updation of Data
    country_ts = country_data['meta']['last_updated'].split('T')[0] + ' ' + country_data['meta']['last_updated'].split('T')[1][:5] + ' IST'


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

    '''Extracting India Data.'''
    ind_table = PrettyTable(summ_head)
    confirmed = country_data['total'].get('confirmed', 0)
    recovered = country_data['total'].get('recovered', 0)
    deceased = country_data['total'].get('deceased', 0)
    tested = country_data['total'].get('tested', 0)

    delta_confirmed = str(confirmed) + '(+' + str(country_data['delta'].get('confirmed', 0)) + ')' if 'delta' in country_data else confirmed
    delta_recovered = str(recovered) + '(+' + str(country_data['delta'].get('recovered', 0)) + ')' if 'delta' in country_data else recovered
    delta_deceased = str(deceased) +  '(+' + str(country_data['delta'].get('deceased', 0)) + ')' if 'delta' in country_data else deceased
    delta_tested = str(tested) + '(+' + str(country_data['delta'].get('tested', 0)) + ')'
    active = confirmed - (recovered + deceased)

    ind_table.add_row([delta_confirmed, active, delta_recovered, delta_deceased, delta_tested])
    ind_stats.add_row([f'{round((recovered/confirmed)*100,2)}%',
                       f'{round((deceased/confirmed)*100,2)}%',
                       f'{round((confirmed/tested)*100,2)}%'])
    
    #Sending SLACK Notification - Country's Data
    india_msg = f"***** INDIA Cases ******\nDate: {country_ts}\nTotal: {confirmed}\nActive: {active}\nRecovered: {recovered}\nTests Done: {tested}\nDeaths: {deceased}"
    if slack_notify:
        Slack.slack_message(india_msg, __file__)

    print(f'{ind_state_table}\n')
    print(f' India Cases Summary (as on {country_ts}) '.center(70,'*'))
    print(f'{ind_table}\n')
    print(f' India Statistics '.center(60,'*'))
    
    print(ind_stats)


def getStateData(state):
    '''Prints the District Level Data of a given State, State Summary and India Summary of Corona Cases.'''
    try:
        #District Summary Table
        head = ['District', 'Total', 'Active', 'Recovered', 'Deceased']
        dist_table = PrettyTable(head)

        try:
            state_data = d[state]
        except:
            print(f'EXCEPTION: No State Found with this Code')

        #CSV Filename and Path
        os.chdir('C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python38\\Corona-Tracker\\')
        state_filename = f'COVID-19_{state_code[state]}_Districts_Data.csv'

        #Writing the Header to the file
        with open(state_filename, 'w') as f:
            writer = csv.writer(f, delimiter=',', lineterminator='\n')
            writer.writerow([x.upper() for x in head])

        #State Timestamp - Denotes the time of Updation
        state_ts = state_data['meta']['last_updated'].split('T')[0] + ' ' + state_data['meta']['last_updated'].split('T')[1][:5] + ' IST'


        
        summ_head = ['Total', 'Active', 'Recovered', 'Deaths', 'Testing Done']
        summ_table = PrettyTable(summ_head)

        #Table that shows the Percentages of categories
        state_stats = PrettyTable(['Recovery', 'Deaths', 'Affected'])

        '''Extracting District wise Data of a State'''
        with open(state_filename, 'a') as f:
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

        print(f'\nFile Created Successfully. <<< {state_filename} >>>\n')

        '''Extracting State's Data.'''
        confirmed = state_data['total'].get('confirmed', 0)
        recovered = state_data['total'].get('recovered', 0)
        deceased = state_data['total'].get('deceased', 0)
        tested = state_data['total'].get('tested', 0)

        #Adding the New Cases If any.
        delta_confirmed = str(confirmed) + '(+' + str(state_data['delta'].get('confirmed', 0)) + ')' if 'delta' in state_data else confirmed
        delta_recovered = str(recovered) + '(+' + str(state_data['delta'].get('recovered', 0)) + ')' if 'delta' in state_data else recovered
        delta_deceased = str(deceased) +  '(+' + str(state_data['delta'].get('deceased', 0)) + ')' if 'delta' in state_data else deceased
        

        active = confirmed - (recovered + deceased)

        summ_table.add_row([delta_confirmed, active, delta_recovered, delta_deceased, tested])
        print(f" Cases across {state_code.get(state, 'Unknown')} (District wise details) ".center(70,'*'))
        print(f'{dist_table}\n')
        print(f' {state_code[state].title()} Cases Summary (as on {state_ts})'.center(70,'*'))
        print(f'{summ_table}\n')

        print(f" {state_code.get(state, 'Unknown').upper()} Statistics ".center(70,'*'))
        state_stats.add_row([f'{round((recovered/confirmed)*100,2)}%',
                             f'{round((deceased/confirmed)*100,2)}%',
                             f'{round((confirmed/tested)*100,2)}%'])

        print(f'{state_stats}\n')

        #Sending SLACK Notification - State's Data
        state_msg = f"***** {state_code.get(state, 'Unknown')} Cases ******\nDate: {state_ts}\nTotal: {confirmed}\nActive: {active}\nRecovered: {recovered}\nTests Done: {tested}\nDeaths: {deceased}"
        if slack_notify:
            Slack.slack_message(state_msg, __file__)


        
    except Exception as e:
        print(f'EXCEPTION: {e}')


#Driver Code - Pass the State Code as the argument.
getStateData('TG')
