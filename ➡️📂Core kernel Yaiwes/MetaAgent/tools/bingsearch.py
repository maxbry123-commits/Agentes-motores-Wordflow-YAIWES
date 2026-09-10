#Copyright (c) Microsoft Corporation. All rights reserved.
#Licensed under the MIT License.
# -*- coding: utf-8 -*-
import json
import os
import requests
os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']=""
subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
endpoint = ""
# Query term(s) to search for.
query = <"Insert your query here">

params = { 'q': query }
headers = { 'Ocp-Apim-Subscription-Key': subscription_key }
# Call the API
try:
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    print("Headers:")
    print(response.headers)
    print("JSON Response:")
    for i in range(3):
        print("The search results are:")
        print(f"{i}:\n")
        print(response.json()['webPages']['value'][i]['snippet'])
except Exception as ex:
    raise ex