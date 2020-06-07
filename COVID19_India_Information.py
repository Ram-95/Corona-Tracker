#COVID 19 India Cases
import requests
import bs4 as bs
import csv
import os
from datetime import date
from prettytable import PrettyTable

os.chdir('C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python38\\Corona-Tracker\\')
filename = 'COVID-19_India_Data.csv'
state_filename = 'COVID-19_State_wise_Information.csv'

today = date.today().strftime("%d-%b-%y")


url = "http://www.mohfw.gov.in/"
response = requests.get(url)
html = response.text
soup = bs.BeautifulSoup(html, 'lxml')

x = soup.find('div', class_= 'status-update').find('span').text.strip()


t_items = soup.find('div', class_= 'data-table').find('table').find('tbody').findAll('tr')
head = ['S.No', 'State/UT', 'Active Cases', 'Discharged', 'Dead', 'Total Cases']

#Creating a Table
ind_table = PrettyTable(head)
summ_table = PrettyTable(['Total', 'Active Cases', 'Discharged', 'Dead', 'Total Cases'])


#Writing the state wise information to a file
with open(state_filename, 'w') as f:
    writer = csv.writer(f, delimiter= ',', lineterminator= '\n')
    writer.writerow([x.upper() for x in head])

#To count the rows until span is found in the <td> tag.
item = 0
for i in t_items:
    state_data = []
    #Stop when span is present in the table row. Because total number of cases are present inside span tag.
    if i.find('span') is None:
        for k in i.findAll('td'):
            state_data.append(k.text.strip())
        if state_data[1] != "Cases being reassigned to states":
            ind_table.add_row(state_data)

        with open(state_filename, 'a') as f:
            writer = csv.writer(f, delimiter=',', lineterminator='\n')
            if state_data[1] != "Cases being reassigned to states":
                writer.writerow(state_data)
        item += 1
    else:
        break


print('\n' + '*'*20 + ' INDIA - STATE WISE INFORMATION (' + x + ') ' + '*'*20)
print(f'{ind_table}')

summ = []
for j in t_items[item].findAll('td'):
    summ.append(j.text.strip())
del summ[0]
summ_table.add_row(summ)

print(f'Summary:\n{summ_table}')



'''Code for writing to the Files.'''

#Creating the CSV File if not already present
files = os.listdir()

deaths = int(summ[3])
total_cases = int(str(summ[4]).replace('#', ''))

if filename not in files:
    with open(filename, 'w') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        writer.writerow(['DATE', 'TOTAL_CASES', 'DEATHS'])
        print(f'\nCSV File Created Successfully.\n')


#Reading the CSV File
with open(filename, 'r') as f:
    reader = csv.reader(f, delimiter=',', lineterminator='\n')
    data = list(reader)
    #print(f'{data}')
    

if data[-1][0] == 'DATE':
    with open(filename, 'a') as f:
        writer = csv.writer(f, delimiter = ',', lineterminator = '\n')
        writer.writerow([today, total_cases, deaths])
        
else:
    if data[-1][0] == today or int(today.split('-')[0]) == int(data[-1][0].split('-')[0]):
        data[-1][1] = str(max(int(data[-1][1].replace(',', '')), total_cases))
        data[-1][2] = str(max(int(data[-1][2].replace(',', '')), deaths))

        with open(filename, 'w') as f:
            wr = csv.writer(f, delimiter= ',', lineterminator='\n')
            for item in data:
                wr.writerow(item)
    else:
        with open(filename, 'a') as f:
            writer = csv.writer(f, delimiter = ',', lineterminator = '\n')
            writer.writerow([today, total_cases, deaths])

ch = input('\n\nDo you want to know Telangana\'s COVID-19 Information ?(y/n): \n')
if ch.lower() == 'y':
    try:
        import COVID19_State_Data as COVID_TS
    except Exception as e:
        print(f'{e}')
