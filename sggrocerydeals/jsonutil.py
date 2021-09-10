import os
import json

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
JSON_FILE = os.path.join(WORKING_DIR, 'processed.json')


def fullTemplate(date, com_id, url_list):
    '''
    Format to json

    date -- Datetime today object
    com_id -- company name
    url_list -- URL string list
    '''

    json_data = [
                    {
                        "date" : str(date),
                        "promo" : promoTemplate(com_id, url_list)
                    }
                ]
    return json_data

def promoTemplate(com_id, url_list):
    '''
    Format to json
    
    com_id -- company name
    url_list -- URL string list
    '''

    json_data = {
                    com_id : url_list
                }
    return json_data


def jsonAppend(date, com_id, url_list, existing_data):
    '''
    Format json data for append

    date -- Datetime today object
    com_id -- company name
    url_list -- URL string list
    existing_data -- last data from json file
    '''

    # same date, append
    if(existing_data[-1]['date'] == str(date)):
        if com_id in existing_data[-1]['promo']:
            # com_id exists, append url
            list = existing_data[-1]['promo'][com_id]
            list.extend(url_list)
            existing_data[-1]['promo'].update(promoTemplate(com_id, list))
        else:
            # todo: com_id does not exist, append to date
            dict = existing_data[-1]['promo']
            existing_data[-1]['promo'].update(promoTemplate(com_id, url_list))
    else:  
        json_data = fullTemplate(date, com_id, url_list)
        existing_data.extend(json_data)

    return existing_data


def jsonAdd(date, com_id, url_list):
    '''
    Format json data

    date -- Datetime today object
    com_id -- company name
    url_list -- URL string list
    '''

    return fullTemplate(date, com_id, url_list)


def saveTodayUrl(date, com_id, url_list):
    '''
    Save date and URL for processed URL

    date -- Datetime today object
    com_id -- company name
    url_list -- URL string list
    '''
    global JSON_FILE

    try:

        if os.path.exists(JSON_FILE):
            with open(JSON_FILE) as file:
                existing_data = json.load(file)
            # append to existing data
            json_data = jsonAppend(date, com_id, url_list, existing_data)
        else:
            # create new file
            json_data = jsonAdd(date, com_id, url_list)

        with open(JSON_FILE, "w") as file:
            json.dump(json_data, file, indent=4)

    except Exception as ex:
        print('Exception while saving json url')
        raise ex


def readLastUrl(com_id):
    '''
    Return the last processed URL
    com_id -- company name
    '''
    global JSON_FILE
    list = []

    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE) as file:
                data = json.load(file)

            ctr = 0
            for idx in range(len(data)-1, -1, -1):
                if com_id in data[idx]['promo']:
                    list.extend(data[idx]['promo'][com_id])
                    ctr += 1
                    if ctr == 5:
                        break

        except Exception as ex:
            print('Exception while getting json past url')
            raise ex

    return list