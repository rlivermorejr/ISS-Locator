#!/usr/bin/env python

__author__ = """Russell Livermore"""

import time
import requests
import json

import reverse_geocoder as rg


naut_res = requests.get('http://api.open-notify.org/astros.json')
locale_res = requests.get('http://api.open-notify.org/iss-now.json')
iss_list = naut_res.json()
locale = locale_res.json()


def jprint(obj):
    """Create a formatted string of the API request JSON object"""
    text = json.dumps(obj, sort_keys=True, indent=4)
    return text


def current_nauts(obj):
    """Formats API object (astronaut list) into string
    then prints in readable format"""
    ast_num = obj['number']
    ast_list = []
    for value in obj['people']:
        if value['craft'] == 'ISS':
            ast_list.append(value['name'])
    print(f"""\nThere are {ast_num} 'nauts on the ISS.\b
Astronauts currently on ISS:\n{ast_list}""")


def current_locale(obj):
    """Formats API object (iss location) into string
    then prints in readable format"""
    timestamp = obj['timestamp']
    lat = obj['iss_position']['latitude']
    lon = obj['iss_position']['longitude']
    readable_time = jprint(time.ctime(timestamp))
    country, city, state, obj = get_country(lat, lon)
    print(f"""\nThe ISS is over {city}, {state} in {country}:\b
At latitude: {lat}\b
and longitude: {lon}\b
{readable_time}""")


def passover(obj, country, city, state):
    """Formats API object (date/time iss passes over Indiana)
    into string then prints in readable format"""
    try:
        timestamp = obj['request']['datetime']
        # altitude seems to always be 100 and that is not correct
        # alt = obj['request']['altitude']
        readable_time = jprint(time.ctime(timestamp))
        print(f"""\nThe ISS will be over\n\
{city}, {state} in {country}\b
At: {readable_time}""")
    except KeyError:
        print("""\nInvalid parameters!\b
Please enter a valid latitude and longitude!""")


def get_country(lat, lon):
    try:
        loc_obj = {
            'lat': lat,
            'lon': lon
        }
        result_obj = []
        df = loc_obj

        passover_res = requests.get(
            'http://api.open-notify.org/iss-pass.json', params=loc_obj)
        passover_json = passover_res.json()
        for i in range(0, len(df)):
            coordinates = (df["lat"], df["lon"])
            result_obj.append(rg.search(coordinates))
        city = result_obj[0][0]['name']
        country = result_obj[0][0]['cc']
        state = result_obj[0][0]['admin1']
        return (country, city, state, passover_json)
    except TypeError:
        return


def main():
    try:
        print("Welcome to my ISS locator application!")
        print("")
        print("If you would like to see where the ISS is right now\n\
and who is on board, enter the word \"now\" for latitude!")
        print("")
        print("Otherwise, enter the latitude and longitude,\n\
and I will tell you when the ISS is passing over!")
        print("")
        lat = input('enter latitude: ')
        if (lat == 'now'):
            current_locale(locale)
            current_nauts(iss_list)
        else:
            lon = input('enter longitutde (don\'t forget the - if needed): ')
            country, city, state, obj = get_country(lat, lon)
            passover(obj, country, city, state)
    except ValueError:
        print("""\nERROR!\b
Please enter correct parameters!""")


if __name__ == '__main__':
    main()
