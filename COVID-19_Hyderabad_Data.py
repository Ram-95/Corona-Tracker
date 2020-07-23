#Hyderabad COVID Cases
import requests
import bs4 as bs
from tabulate import tabulate

url = 'https://www.ghmc.gov.in/covid_details.aspx'

response = requests.get(url)
html = response.text
soup = bs.BeautifulSoup(html, 'lxml')

key = 'Kapra-01'
table = soup.find('table', class_='clsGrid')
head = []
for i in table.select_one('tr:nth-of-type(1)').findAll('th'):
    head.append(i.text.strip())


items = table.findAll('tr', class_='clsAltItemGrid')

count = 0
res = []
for i in items:
    temp = []
    if i.select_one('td:nth-of-type(5)').text.strip() == key:
        for j in range(1,7):
            temp.append(i.select_one('td:nth-of-type('+ str(j) + ')').text.strip())
        count += 1
        res.append(list(temp))


print(tabulate(res, headers=head, tablefmt='fancy_grid'))
print(f'\nTotal Cases in {key}: {count}')

