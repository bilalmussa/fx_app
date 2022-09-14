#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 09:26:42 2022

@author: bilal.mussa
"""

import streamlit as st
import numpy as np
import requests
import json
import pandas as pd
import ast
from st_aggrid import AgGrid

st.set_page_config(layout='wide')

st.title("FX Rate Comparison by major providers")
st.write("**By: [Bilal Mussa](https://www.linkedin.com/in/bilalmussa/)**")
st.write("This app is a proof of concept for a potential website where individuals and businesses can compare fx rates by the major providers"
         "Eventually we'd like to embed affiliate links too if/when we go live as well as provide content on travelling/travels")

st.sidebar.write('Please select your home currency and receiving currency')

home_curr = ['USD','GBP']

rec_curr = ['INR','CNY', 'ZAR']

countries = {'USD':'USA'
             ,'GBP':'GBR'
             ,'INR': 'IND'
             , 'CNY': 'CHN'
             , 'ZAR': 'ZAF'
             }

params = {
    'source': 'EUR',
    'target': 'USD',
}

option = st.sidebar.selectbox('Select your home currency?',
                      (home_curr))

st.sidebar.write('You selected:', option)

option2 = st.sidebar.selectbox('Select your receiving currency?',
                      (rec_curr))

st.sidebar.write('You selected:', option2)

from_country_selected = countries[option]
send_country_selected = countries[option2]

option3 = st.sidebar.number_input('How much would you like to send?',min_value=100, step=100)

#url = 'https://api.transferwise.com/v1/rates?source=EUR&target=USD'
#response = requests.get(url
#                        ,auth=('bilal-mussa', '72917072-7CAA-4E8D-BFCC-F0ECCFD8503D'))
#print(response.status_code)

#this may be a good option to use?
url = 'https://api.transferwise.com/v3/comparisons/?sourceCurrency='+option+'&targetCurrency='+option2+'&sendAmount='+str(option3)

#print(url)
response = requests.get(url
                        ,auth=('bilal-mussa', '72917072-7CAA-4E8D-BFCC-F0ECCFD8503D'))
#print(response.status_code)
data = response.text
data = json.loads(data)
wise_data = pd.DataFrame(data['providers'])[['name','quotes']]

wise_data['quotes']=wise_data['quotes'].astype(str).str[1:-1]
wise_data['quotes'] = wise_data['quotes'].apply(lambda x: ast.literal_eval(x))

df2 = pd.json_normalize(wise_data['quotes'])

wise_data= pd.concat([wise_data,df2], axis=1)

wise_data= wise_data[['name','rate','fee','receivedAmount']]

#remitly

url = 'https://prices.remitly.com/v1/price?from_currency='+option+'&to_currency='+option2+'&from_country='\
    +from_country_selected+'&to_country='+send_country_selected+'&send_amount='+str(option3)+'&package=economy&new_customer=false'
headers = {'X-API-KEY': 'rStHcZgJYOWcdXFmyBW54IJNjooSJQUf'}
response = requests.get(url
                        ,headers=headers)
#print(response.status_code)
data1 = response.text
data1=json.loads(data1)
#print(data1)
remitly_data = pd.DataFrame(data1,index=[0])

remitly_fee = pd.to_numeric(remitly_data['fee'],errors='coerce')[0]
remitly_rate = pd.to_numeric(remitly_data['rate'],errors='coerce')[0]

remitly_data = {'name': 'Remitly'
                , 'rate': remitly_rate
                , 'fee': remitly_fee
                , 'receivedAmount': remitly_rate*(option3-remitly_fee)
                }
                                      
wise_data.loc[len(wise_data.index)] = [remitly_data['name'],remitly_data['rate'],remitly_data['fee'],remitly_data['receivedAmount']]

wise_data=wise_data.sort_values(by=['receivedAmount'],ascending=False)

wise_data['url']= ""
wise_data.loc[wise_data['name']=='Remitly','url'] = 'https://remitly.tod8mp.net/KebZb7'

def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = 'click here'
    return f'<a target="_blank" href="{link}">{text}</a>'

# link is the column with hyperlinks
wise_data['url'] = wise_data['url'].apply(make_clickable)
wise_data = wise_data.to_html(escape=False)
st.write(wise_data, unsafe_allow_html=True)

#wise_data.style.format({'url': make_clickable})

#AgGrid(wise_data, height=500, fit_columns_on_grid_load=True)

#st.write(wise_data.to_html(escape=False, index=False), unsafe_allow_html=True)

wise_data = pd.read_html(wise_data)[0]

st.write('The best provider is:', wise_data['name'].iloc[0])
