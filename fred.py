# @Author: DivineEnder
# @Date:   2018-07-29 19:24:08
# @Email:  danuta@u.rochester.edu
# @Last modified by:   DivineEnder
# @Last modified time: 2018-07-29 23:18:00

import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

def parse_param(param_soup):
	param = {}
	# Whether param is required
	param['required'] = param_soup['class'] is "required"
	# Parse paramter soup information
	for param_attrs_soup in param_soup.find_all('td'):
		if param_attrs_soup['class'][0] == 'name' or param_attrs_soup['class'][0] == 'type':
			param[param_attrs_soup['class'][0]] = param_attrs_soup.text
		# Parse paramter description (have to pull out of paragraph text)
		elif param_attrs_soup['class'][0] == 'description':
			param[param_attrs_soup['class'][0]] = param_attrs_soup.find('p').text.replace("\n", "")
		# Parse parameter options
		elif param_attrs_soup['class'][0] == 'parameter':
			param['options'] = list(map(lambda op: op.text, param_attrs_soup.find_all('option')))
		else:
			print(param_attrs_soup['class'][0])
			raise ValueError("Bad paramter info")

	return param

def parse_endpoint_method(method_soup):
	method = {}
	# Get method description attributes
	for method_attrs_soup in method_soup.find('div').find_all('span'):
		method[method_attrs_soup['class'][0]] = method_attrs_soup.text
	# Description does not follow standard format (not in title HTML tag for some reason)
	method['description'] = method_soup.find('span', attrs = {'class': 'description'}).text

	# Check whether this method has any parameters
	if method_soup.find('tbody'):
		# Extract method parameters by applying parsing function to each soup param
		method['params'] = list(map(lambda param_soup: parse_param(param_soup), method_soup.find('tbody').find_all('tr')))

	return method

def parse_endpoint(endpoint_soup):
	endpoint = {}
	# Get the name of the HTML list of endpoints
	endpoint['name'] = endpoint_soup.find('h3').find('span').text
	# Parse endpoint methods by applying parsing function to each soup method
	endpoint['methods'] = list(map(lambda method_soup: parse_endpoint_method(method_soup), endpoint_soup.find_all('li', attrs = {'class': ['method', 'get', '']})))

	return endpoint

if __name__ == '__main__':
	r = requests.get("https://www.federalregister.gov/developers/api/v1")
	soup = BeautifulSoup(r.content, 'html.parser')
	endpoint_soups = soup.find_all('li', attrs = {'class': ['endpoint', 'expanded']})

	endpoints = {}
	endpoints['base_uri'] = "www.federalregister.gov/api/v1"
	endpoints['endpoints'] = []
	# Get the HTML list of endpoints
	for endpoint_soup in endpoint_soups:
		endpoint = parse_endpoint(endpoint_soup)
		endpoints['endpoints'].append(endpoint)

	# Dump parsed endpoints to json file
	json.dump(endpoints, open("FRED-{}.json".format(datetime.now().strftime("%Y-%m-%d")), "w"), indent = 2)
