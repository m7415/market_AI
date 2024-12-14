import requests
import os
import sys
import pandas as pd
import json
import time

URL_DATA_CENTERS = "https://universalis.app/api/v2/data-centers"
URL_WORLDS = "https://universalis.app/api/v2/worlds"
URL_TAX_RATES = "https://universalis.app/api/v2/tax-rates"
URL_CURRENT_DATA = "https://universalis.app/api/v2"
URL_HISTORICAL_DATA = "https://universalis.app/api/v2/history"

def get_data_centers():
    response = requests.get(URL_DATA_CENTERS)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        sys.exit(1)
    return response.json()

def get_worlds():
    response = requests.get(URL_WORLDS)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        sys.exit(1)
    return response.json()

def get_tax_rates(id):
    url = f"{URL_TAX_RATES}?world={id}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        sys.exit(1)
    return response.json()

def get_target_worlds(data_center):
    data_centers = get_data_centers()
    worlds = get_worlds()

    target_worlds = []

    for world in worlds:
        if world['id'] in data_centers[data_center]['worlds']:
            target_worlds.append((world['id'], world['name'], {}))

    for world in target_worlds:
        tax_rates = get_tax_rates(world[0])
        target_worlds[target_worlds.index(world)] = (world[0], world[1], tax_rates)
    
    return target_worlds

def get_history(worldDcRegion, itemId, entriesToReturn, statsWithin, entriesWithin):
    url = f"{URL_HISTORICAL_DATA}/{worldDcRegion}/{itemId}?entries={entriesToReturn}&statsWithin={statsWithin}&entriesWithin={entriesWithin}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        sys.exit(1)
    return response.json()

def get_current_data(worldDcRegion, itemIds, listings, hq, statsWithin, fields):
    url = f"{URL_CURRENT_DATA}/{worldDcRegion}/{itemIds}?listings={listings}&hq={hq}&statsWithin={statsWithin}&fields={fields}"
    response = requests.get(url)

    # if the server is busy, wait and try again
    tryout = 0
    while (response.status_code == 500 or response.status_code == 504) and tryout < 10:
        time.sleep(0.05)
        response = requests.get(url)
        tryout += 1

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        # print the parameters to debug
        print(f"worldDcRegion: {worldDcRegion}")
        print(f"itemIds: {itemIds}")
        sys.exit(1)
    return response.json()