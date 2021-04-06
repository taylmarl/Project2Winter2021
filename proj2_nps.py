#################################
##### Name: Taylor Marlin #######
##### Uniqname: taylmarl  #######
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

BASE_URL = 'https://www.nps.gov'
CACHE_FILENAME = "nationalparks.json"
CACHE_DICT = {}

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()


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

    if BASE_URL in CACHE_DICT.keys():
        print("Using cache")
        response = CACHE_DICT[BASE_URL]
        soup = BeautifulSoup(response, 'html.parser')
    else:
        # Request from baseurl and use bs4 to parse html
        print("Fetching")
        response = requests.get(BASE_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        CACHE_DICT[BASE_URL] = response.text
        save_cache(CACHE_DICT)

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

    if site_url in CACHE_DICT.keys():
        print("Using cache")
        response = CACHE_DICT[site_url]
        soup = BeautifulSoup(response, 'html.parser')
    else:
        # Get soup from national site url
        print("Fetching")
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        CACHE_DICT[site_url] = response.text
        save_cache(CACHE_DICT)

    # Find Name and Category using a parent class to narrow scope
    name_cat_parent = soup.find('div', class_='Hero-titleContainer clearfix')

    if len(name_cat_parent.find('a').contents) > 0:
        name = name_cat_parent.find('a').contents[0]
    else:
        name = "No Name"

    category_parent = name_cat_parent.find('div', class_='Hero-designationContainer')

    if len(category_parent.find('span', class_='Hero-designation').contents) > 0:
        category = category_parent.find('span', class_='Hero-designation').contents[0]
    else:
        category = "No Category"


    # Find contact & location information using a parent class to narrow scope
    contact_parent = soup.find('div', class_='vcard')
    if contact_parent.find('span', itemprop='addressLocality') is not None:
        if len(contact_parent.find('span', itemprop='addressLocality').contents) > 0:
            city = contact_parent.find('span', itemprop='addressLocality').contents[0]
        else:
            city = "No City"
    else:
        city = "No City"

    if contact_parent.find('span', class_='region') is not None:
        if len(contact_parent.find('span', class_='region').contents) > 0:
            region = contact_parent.find('span', class_='region').contents[0]
        else:
            region = "No Region"
    else:
        region = "No Region"
    address = city + ', ' + region

    if contact_parent.find('span', class_='postal-code') is not None:
        if len(contact_parent.find('span', class_='postal-code').contents) > 0:
            zipcode = contact_parent.find('span', class_='postal-code').contents[0]
        else:
            zipcode = "No Zipcode"
    else:
        zipcode = "No Zipcode"

    if contact_parent.find('span', class_='tel') is not None:
        if len(contact_parent.find('span', class_='tel').contents) > 0:
            telephone = contact_parent.find('span', class_='tel').contents[0]
        else:
            telephone = "No Telephone"
    else:
        telephone = "No Telephone"

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
    url_list = []
    national_site_objs = []

    if state_url in CACHE_DICT.keys():
        print("Using cache")
        response = CACHE_DICT[state_url]
        soup = BeautifulSoup(response, 'html.parser')
    else:
        print("Fetching")
        response = requests.get(state_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        CACHE_DICT[state_url] = response.text
        save_cache(CACHE_DICT)
    # print(CACHE_DICT)

    # Find results list of links using parent class to narrow scope
    park_results = soup.find('div', id='parkListResultsArea')
    park_list_urls = park_results.find_all('li', class_='clearfix')

    # Obtain list of urls for each national site in given state
    for list_item in park_list_urls:
        path = list_item.find('a')['href']
        url_list.append(BASE_URL + path)

    # iterate through site urls, call get_site_instance(), and return list of each object
    for url in url_list:
        site_obj = get_site_instance(url)
        national_site_objs.append(site_obj)

    return national_site_objs

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
    # print(build_state_url_dict())
    # get_site_instance('https://www.nps.gov/yell/index.htm')

    CACHE_DICT = open_cache()
    state_url_dict = build_state_url_dict()

    state_name = input(f"Please input a state name (e.g. Michigan, michigan) or 'exit': ")
    state_name = state_name.lower()


    # Was that a valid input? This would check.
    while True:
        if state_name in state_url_dict.keys():
            # use dictionary to get url
            state_url = state_url_dict[state_name]
            break
        elif state_name == 'exit':
            print("\nBye!")
            break
        else:
            print("\nInvalid input - state not found. Please try again.")
            state_name = input(f"Please input a state name (e.g. Michigan, michigan) or 'exit': ")

    # Get object instances for state parks
    nat_sites = get_sites_for_state(state_url)

    # Print header text to display list of national parks
    print("------------------------------------------")
    print(f"List of national sites in {state_name.title()}")
    print("------------------------------------------")

    # Iterate using counting and .info() method to print formatted results
    count = 1
    for i in range(len(nat_sites)):
                print(f"[{count}] {nat_sites[i].info()}")
                count += 1