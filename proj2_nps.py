#################################
##### Name: Taylor Marlin #######
##### Uniqname: taylmarl  #######
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets as pysecrets # file that contains your API key

# National Parks base url
BASE_URL = 'https://www.nps.gov'

# Map Quest Radius Search base url
MAPQ_URL = 'http://www.mapquestapi.com/search/v2/radius'

CACHE_FILENAME = "nationalparks.json"
CACHE_DICT = {}

client_key = pysecrets.MAPQ_API_KEY


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
        '''
        Initalize instance of National Site according to class spec.
        '''
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    
    def info(self):
        '''
        Return nicely formatted information about National Site object.
        '''
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

    # Use Caching when applicable to save time & requests
    if BASE_URL in CACHE_DICT.keys():
        print("Using cache")
        response = CACHE_DICT[BASE_URL]
        soup = BeautifulSoup(response, 'html.parser')
    else:
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

    # Use Caching when applicable to save time & requests
    if site_url in CACHE_DICT.keys():
        print("Using cache")
        response = CACHE_DICT[site_url]
        soup = BeautifulSoup(response, 'html.parser')
    else:
        print("Fetching")
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        CACHE_DICT[site_url] = response.text
        save_cache(CACHE_DICT)

    # Find Name and Category using a parent class to narrow scope
    name_cat_parent = soup.find('div', class_='Hero-titleContainer clearfix')

    # If attribute is not available for a site, create placeholder str
    if name_cat_parent is not None:
        if len(name_cat_parent.find('a').contents) > 0:
            name = name_cat_parent.find('a').contents[0]
        else:
            name = "No Name"
    else:
            name = "No Name"

    # Narrow scope further to obtain category parent div 
    if name_cat_parent is not None and name_cat_parent.find('div', class_='Hero-designationContainer') is not None:
        category_parent = name_cat_parent.find('div', class_='Hero-designationContainer')
    else:
        category_parent = name_cat_parent

    # If attribute is not available for a site, create placeholder str
    if category_parent is not None and category_parent.find('span', class_='Hero-designation') is not None:
        if len(category_parent.find('span', class_='Hero-designation').contents) > 0:
            category = category_parent.find('span', class_='Hero-designation').contents[0]
        else:
            category = "No Category"
    else:
            category = "No Category"


    # Find contact & location information using a parent class to narrow scope
    contact_parent = soup.find('div', class_='vcard')

    # If attribute is not available for a site, create placeholder str
    if contact_parent is not None and contact_parent.find('span', itemprop='addressLocality') is not None:
        if len(contact_parent.find('span', itemprop='addressLocality').contents) > 0:
            city = contact_parent.find('span', itemprop='addressLocality').contents[0]
        else:
            city = "No City"
    else:
        city = "No City"

    # If attribute is not available for a site, create placeholder str
    if contact_parent is not None and contact_parent.find('span', class_='region') is not None:
        if len(contact_parent.find('span', class_='region').contents) > 0:
            region = contact_parent.find('span', class_='region').contents[0]
        else:
            region = "No Region"
    else:
        region = "No Region"

    address = city + ', ' + region

    # If attribute is not available for a site, create placeholder str
    if contact_parent is not None and contact_parent.find('span', class_='postal-code') is not None:
        if len(contact_parent.find('span', class_='postal-code').contents) > 0:
            zipcode = contact_parent.find('span', class_='postal-code').contents[0]
        else:
            zipcode = "No Zipcode"
    else:
        zipcode = "No Zipcode"

    # If attribute is not available for a site, create placeholder str
    if contact_parent is not None and contact_parent.find('span', class_='tel') is not None:
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


    # Use caching to save time & requests
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

    # Find results <li> of links using parent class to narrow scope
    park_results = soup.find('div', id='parkListResultsArea')
    park_list_urls = park_results.find_all('li', class_='clearfix')

    # Obtain python list of urls for each national site in given state
    for list_item in park_list_urls:
        path = list_item.find('a')['href']
        url_list.append(BASE_URL + path)

    # Create instance for each national site url in our list
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
    params = {'radius': '10',
              'units': 'm',
              'maxMatches': '10',
              'ambiguities': 'ignore',
              'outFormat': 'json',
              'key': client_key,
              'origin': site_object.zipcode}
    
    # Caching
    if site_object.zipcode in CACHE_DICT.keys():
        print("Using cache")
        results = CACHE_DICT[site_object.zipcode]
    else:
        print("Fetching")
        response = requests.get(MAPQ_URL, params)
        results = response.json()
        CACHE_DICT[site_object.zipcode] = results
        save_cache(CACHE_DICT)

    return results

def format_nearby_places(json_results):
    '''Parse MapQuest API results and print nearby places.
    
    Parameters
    ----------
    json_results: dict
        dictionary containing response from MapQuest API
    '''
    # verify that this key is valid
    if 'searchResults' in json_results.keys():
        list_dict_nearby = json_results['searchResults']
    else:
        return "No valid results."

    # Iterate through list of dictionaries containing nearby places & get fields
    for i in range(len(list_dict_nearby)):
        name = list_dict_nearby[i]['name']
        category = list_dict_nearby[i]['fields']['group_sic_code_name']
        address = list_dict_nearby[i]['fields']['address']
        city = list_dict_nearby[i]['fields']['city']

        # Replace blank fields with str statements
        if name == '':
            name = 'No Name'
        if category == '':
            category = 'No Category'
        if address == '':
            address = 'No Address'
        if city == '':
            city = 'No City'

        # Print each place in a nice format
        print(f"- {name} ({category}): {address}, {city}")
    

if __name__ == "__main__":

    CACHE_DICT = open_cache()
    state_url_dict = build_state_url_dict()

    # Ask for user input and make it lowercase for the dictionary
    state_name = input(f"Please input a state name (e.g. Michigan, michigan) or 'exit': ")
    state_name = state_name.lower()

    # Use indicator variable to indicate when to 
    # have user enter search term & how to use 'back' feature
    indicator = True

    while True:
        if state_name == 'exit':
            print("\nBye!")
            break

        # Was the user input valid? This would check.
        elif state_name in state_url_dict.keys():
            if indicator:
                # use dictionary to get url
                state_url = state_url_dict[state_name]
                # Get object instances for state parks
                nat_sites = get_sites_for_state(state_url)

                # Print header text to display list of national parks
                print("----------------------------------------")
                print(f"List of national sites in {state_name.title()}")
                print("----------------------------------------")

                # Iterate using counting and .info() method to print formatted results
                count = 1
                for i in range(len(nat_sites)):
                            print(f"[{count}] {nat_sites[i].info()}")
                            count += 1

            # Change status of indicator so this code
            # does not run after successful search,
            # unless user enters 'back' (further down in code)
            indicator = False

            while True:
                detail_num = input(f"\nChoose a number in the list for more details, or type 'exit' or 'back': ")
                if detail_num.isnumeric() and int(detail_num) > 0 and int(detail_num) < count:
                    # Print header text to display list of national parks
                    print("----------------------------------------")
                    print(f"Places near {nat_sites[int(detail_num) - 1].name}")
                    print("----------------------------------------")
                    data = get_nearby_places(nat_sites[int(detail_num) - 1])
                    format_nearby_places(data)

                elif detail_num == 'back':
                    state_name = input(f"\nPlease input a state name (e.g. Michigan, michigan) or 'exit': ")
                    state_name = state_name.lower()
                    indicator = True
                    break

                elif detail_num == 'exit':
                    state_name = 'exit'
                    break

                # For any 'invalid' input or state not on the website, reprompt user
                else:
                    print("\n[Error] Invalid input")

        else:
            print("\n[Error] Enter proper state name")
            state_name = input(f"\nPlease input a state name (e.g. Michigan, michigan) or 'exit': ")
            state_name = state_name.lower()
