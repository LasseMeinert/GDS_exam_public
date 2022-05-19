from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import re
import pandas as pd


def get_air_pollution(html):
    air_pollution = []
    
    indeces = [m.start() for m in re.finditer('Luftkoncentrationen af',html)]
    
    #if there aren't any indeces
    if not len(indeces):
        return [None,None,None,None]
    
    for i in indeces:
        string = html[i:i+100]
        found = re.findall("\d+\.\d+", string)
        if len(found) > 1:
            air_pollution.append(float(found[1]))
        else:
            air_pollution.append(float(found[0]))
            
    return air_pollution


def get_noise_pollution(html):
    try:
        noise_polution_index = [m.start() for m in re.finditer('er vurderet',html)]
        noise_polution_index = noise_polution_index[0]
    
        string = html[noise_polution_index:noise_polution_index+50]
        found = re.findall("\d+\-\d+", string)
        noise_pollution = found[0]
    except:
        noise_pollution = '< 55'
    
    return noise_pollution


def get_energy_label(html):
    try:
        energy_label_index = [m.start() for m in re.finditer('har energimærke',html)]
        energy_label_index = energy_label_index[0]

        string = html[energy_label_index:energy_label_index+20]
        found = re.findall("[A-Z]", string)
        energy_label = found[0]
    except: 
        energy_label = "Unknown"
    
    return energy_label


def get_pollution(url):
    r = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(r).read()
    
    html = response.decode("utf-8")
    
    air_pollution = get_air_pollution(html)
    noise_pollution = get_noise_pollution(html)
    energy_label = get_energy_label(html)
        
    return air_pollution, noise_pollution, energy_label

def convert_weird_letters(string):
    mapp = {'ø':'%C3%B8',
            'æ':'%C3%A6',
            'å':'%C3%A5',
            'é':'%C3%A9',
            'ü':'%C3%BC',
            'ë':'%C3%AB',
            'ä':'%C3%A4',
            'ö':'%C3%B6',
            
           }

    for k,v in mapp.items():
        string = string.replace(k,v)
    
    return string

def prepare_df(df):
    df['kommune'] = ['-'.join(x) for x in [x.lower().split(' ') for x in df['city'].tolist()]]
    df['address_url'] = df['postal'].astype(str) + '-' + df['kommune'].astype(str)
    
    df['tmp_address'] = ['/'.join(x) for x in [x.lower().replace('.','').replace(' ','-').split(',-') for x in df['address'].tolist()]]
    df['final_url'] = 'https://www.dingeo.dk/adresse/' + df['address_url'].astype(str) + '/' + df['tmp_address'].astype(str)
    
    df['final_url'] = df['final_url'].apply(lambda x: convert_weird_letters(x))
    return df

