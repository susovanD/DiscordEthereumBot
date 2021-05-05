# -*- coding: utf-8 -*-
"""
Created on Sun May  2 15:27:23 2021

@author: ASUS
"""
import random
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import discord
from discord.ext import tasks
from itertools import cycle
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()
token=os.getenv('Token')
time_repeat=100
url="https://etherscan.io/contractsVerified/1?ps=100"

def get_UserAgent():
    ua=['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
        'Mozilla/5.0 (Linux; Android 5.0; SM-G920A) AppleWebKit (KHTML, like Gecko) Chrome Mobile Safari (compatible; AdsBot-Google-Mobile; +http://www.google.com/mobile/adsbot.html)'
    ]
    return random.choice(ua)

def get_html(proxies,url):
    '''
    This code will load proxies and use them for requests.
    Proxies are scraped from :
    '''
    user_agent_desktop=get_UserAgent()
    headers = {'User-Agent': user_agent_desktop}
    counter=0
    while counter<=10:
        #get the proxy
        ip=random.choice(proxies)
        #get session
        s=requests.session()
        s.Proxies={'http':ip,'https':ip}
        try:
            val=s.get(url,headers=headers)
            break
        except :
            counter+=1
            if counter>10:
                print("10 proxies failed")
    return val

def get_proxy():
    urls=["https://sslproxies.org/","https://free-proxy-list.net/"]
    proxies=[]
    for url in urls:
        html_data=requests.get(url)
        soup=BeautifulSoup(html_data.content,'lxml')
        proxy_list=soup.tbody.find_all('tr')
        for row in proxy_list:
            host=row.find_all('td')[0].text.strip()
            port=row.find_all('td')[1].text.strip()
            ip=f'{host}:{port}'
            proxies.append(ip)
    proxies=list(set(proxies))
    return proxies


def scrape_data(url):
    '''Scrape data from the provided url and saves it in a csv'''
    data=get_html(get_proxy(),url)
    soup=BeautifulSoup(data.content,'lxml')
    total_number_of_pages=int(soup.find_all('li',class_='page-item disabled')[2].text.replace("Page 1 of ",""))
    df_list=[]
    for count in range(total_number_of_pages):
        url=f"https://etherscan.io/contractsVerified/{count}?ps=100"
        data=get_html(get_proxy(),url)
        soup=BeautifulSoup(data.content,'lxml')
        df_list.append(pd.read_html(data.content)[0])
    df_final=pd.concat(df_list)
    #save in csv
    file_name=f'ethereum_contracts.csv'#_{int(time.time())}.csv'
    df_final.to_csv(file_name)
    print("Data Scraping Completed.")
    return file_name
        
class MyClient(discord.Client):

   async def on_ready(self):
       print(f"We have logged in as {self.user}")
       
   async def on_message(self,message):
       if message.author==self.user:
           return
       elif message.content.startswith('hello'):
           await message.channel.send('hello! My name is : '+str(self.user.name) + '\n I will send you the latest Ethereum contract details.:yum: Type <<start>> to enable and <<stop>> to disable.')
       elif message.content.startswith('start'):
           self.is_running=True
           while self.is_running:
               print("Inside while loop")
               file_name=scrape_data(url)
               file = discord.File(file_name)
               if self.is_running:
                   asyncio.sleep(15)
                   await message.channel.send(file=file, content="Latest Ethereum contracts")
               else:
                   print("Execution Stopped as per request.")
                   await message.channel.send('Execution Stopped.')
               
       elif message.content.startswith('stop'):
           self.is_running=False
    # @client.event
#    @tasks.loop(seconds=time_repeat)
#    async def myLoop():

if __name__=="__main__":
    client=MyClient()
    client.run(token)