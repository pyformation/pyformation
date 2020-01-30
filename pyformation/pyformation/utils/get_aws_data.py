import requests
from bs4 import BeautifulSoup
from pyformation import settings
import json


def get_regions():
    regions = []
    s = requests.Session()
    resp = s.get('https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.partial.html')
    soup = BeautifulSoup(resp.content, 'lxml')
    table = soup.find('table')
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) > 1:
            regions.append({'name': cells[0].text, 'value': cells[1].text})
    return regions


def get_specifications():
    s = requests.Session()
    resp = s.get('https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.partial.html')
    soup = BeautifulSoup(resp.content, 'lxml')
    table = soup.find('table')
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) > 1:
            with open('{}{}.json'.format(settings.DEFAULT_SPEC_LIB,cells[1].text.replace('\n','')), 'w') as f:
                resp = s.get(cells[2].p.a['href'])
                data = resp.json()
                json.dump(data, f)
    return
