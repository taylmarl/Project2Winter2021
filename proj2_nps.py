#################################
##### Name: Taylor Marlin #######
##### Uniqname: taylmarl  #######
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

BASE_URL = 'https://www.nps.gov'


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    
    def __init__(self, category, name, address, zipcode, phone):
        #ADD DOCSTRING
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    
    def info(self):
        #ADD DOCSTRING
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"



def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    state_url_dict = {}

    # Request from baseurl and use bs4 to parse html
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # obtain information at parent div level, then isolate the list elements of this class
    state_url_parent = soup.find('div', class_='SearchBar-keywordSearch input-group input-group-lg')
    state_url_lists = state_url_parent.find_all('li')

    # loop through each list item and obtain state name and corresponding url
    for li in state_url_lists:
        url_path = li.find('a')['href']
        state = li.find('a').contents[0]
        state_url_dict[state.lower()] = BASE_URL + url_path

    return state_url_dict

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    # Get soup from national site url
    response = requests.get(site_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find Name and Category using a parent class to narrow scope
    name_cat_parent = soup.find('div', class_='Hero-titleContainer clearfix')

    name = name_cat_parent.find('a').contents[0]
    category_parent = name_cat_parent.find('div', class_='Hero-designationContainer')
    category = category_parent.find('span', class_='Hero-designation').contents[0]


    # Find contact & location information using a parent class to narrow scope
    contact_parent = soup.find('div', class_='vcard')

    city = contact_parent.find('span', itemprop='addressLocality').contents[0]
    region = contact_parent.find('span', class_='region').contents[0]
    address = city + ', ' + region

    zipcode = contact_parent.find('span', class_='postal-code').contents[0]

    telephone = contact_parent.find('span', class_='tel').contents[0]

    # Create and return NationalSite instance
    return NationalSite(category, name, address, zipcode, telephone)

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    pass


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    pass
    

if __name__ == "__main__":
    #print(build_state_url_dict())
    get_site_instance('https://www.nps.gov/yell/index.htm')
    pass