import os
import json

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
JSON_FILE = os.path.join(WORKING_DIR, 'processed.json')


def fullTemplate(date, com_id, url_list):
    '''
    Format to json

    date -- Datetime today object
    url_list -- URL string list
    '''

    json_data = [
                    {
                        "date" : str(date),
                        "promo" : [
                            promoTemplate(com_id, url_list)
                        ]
                    }
                ]
    return json_data

def promoTemplate(com_id, url_list):
    '''
    Format to json
    
    com_id -- company id
    url_list -- URL string list
    '''

    json_data = {
                    "com_id" : com_id,
                    "url": url_list
                }
    return json_data


def jsonAppend(date, com_id, url_list, existing_data):
    '''
    Format json data for append

    date -- Datetime today object
    url_list -- URL string
    '''

    # same date, append
    if(existing_data[-1]['date'] == str(date)):
        existing_data[-1]['promo'].append(promoTemplate(com_id, url_list))
    else:  
        json_data = fullTemplate(date, com_id, url_list)
        existing_data.extend(json_data)

    return existing_data

def jsonAdd(date, com_id, url_list):
    '''
    Format json data

    date -- Datetime today object
    url_list -- URL string
    '''

    return fullTemplate(date, com_id, url_list)

def saveTodayUrl(date, com_id, url_list):
    '''
    Save date and URL for processed URL

    date -- Datetime today object
    url_list -- URL string
    json_file -- json filename
    '''
    global JSON_FILE

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE) as file:
            existing_data = json.load(file)
        json_data = jsonAppend(date, com_id, url_list, existing_data)
    else:
        # create new file
        json_data = jsonAdd(date, com_id, url_list)

    with open(JSON_FILE, "w") as file:
        json.dump(json_data, file, indent=4)
    return

def readLastUrl(com_id):
    '''
    Return the last processed URL
    '''
    global JSON_FILE

    try:
        with open(JSON_FILE) as file:
            data = json.load(file)
        
        list = [com for com in data[-1]['promo'] if com_id in com['com_id']]

        # should only be one
        return list[0]['url']
    except:
        return ''