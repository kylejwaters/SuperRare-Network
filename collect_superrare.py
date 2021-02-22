# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 21:44:23 2021

@author: kylej
"""

#Import libraries 
import pandas as pd
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
from datetime import datetime 
import numpy as np
import time

def get_top_artists(p_chromedriver):

    #Get top artists from SuperRare    

    #Add Chrome options, headers 
    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")
    opts.add_argument("--headless")  
    
    #Start Selenium Webdriver - Change Path as Needed 
    browser = webdriver.Chrome(executable_path = p_chromedriver, chrome_options=opts)

    #Navigate to Superrare 
    superrare_url_artists = "https://superrare.co/top-artists"
    browser.get(superrare_url_artists)
    time.sleep(5)
    
    #Get top artists data
    cols = ["Artist", "Total Sales", "Works Created", "Works Sold", 
            "Highest Sale", "Avg. Sale Price", "Secondary Market Sales", 
            "Avg Secondary Market Price", "Highest Secondary Market Price"]

    df_top_artists = pd.DataFrame(columns=cols)

    artist_count = 0
    while True:
        
        artist_count+=1
        try:
            
            for i, col in enumerate(cols):
                i+=1
                
                #Artist name/profile
                if i == 1:
                    xpath = '//*[@id="root"]/div/div/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[{}]/a'.format(artist_count,i)   
                
                    #Add data
                    df_top_artists.loc[artist_count,col] = browser.find_element_by_xpath(xpath).get_attribute('href')                
                
                #Other data
                else:
                    xpath = '//*[@id="root"]/div/div/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[{}]'.format(artist_count,i)   
                
                    #Add data 
                    df_top_artists.loc[artist_count,col] = browser.find_element_by_xpath(xpath).text                
            
        except:
            break
    
    browser.close()        
    return df_top_artists

def crawl_artist_profiles(p_chromedriver, p_out, df):
    
    #Add Chrome options, headers 
    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")
    opts.add_argument("--headless")  
    
    #Start Selenium Webdriver - Change Path as Needed 
    browser = webdriver.Chrome(executable_path = p_chromedriver, chrome_options=opts)

    #Navigate to Superrare 
    superrare_url_artists = "https://superrare.co"
    browser.get(superrare_url_artists)
    time.sleep(5)
   
    #crawl through each artist's page
    artists_links = df.Artist.values   
    
    df_collector_artist_pairs = pd.DataFrame()
    counter = 0
    number=0
    total = len(artists_links)
    for artist_link in artists_links:
        number+=1
        print("Working on {}, {} of {}.".format(artist_link,number,total))
        browser.get(artist_link)
        time.sleep(7)

        #navigate to works by that artist
        
        try:
            
            browser.find_element_by_xpath('//*[@id="simple-tab-panel-0"]/div[2]/a').click()
            time.sleep(8)
            
            #######################
            #Scroll to Bottom
            #######################
            SCROLL_PAUSE_TIME = 0.5
            
            # Get scroll height
            last_height = browser.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll down to bottom
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)
            
                # Calculate new scroll height and compare with last scroll height
                new_height = browser.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                    
            #Get collectors for that artists' works 
            artwork_counter = 1
            while True:
                
                artwork_counter+=1
                
                try:
                    #Info on that artwork
                    xpath_artwork_name = '//*[@id="root"]/div/div/div[2]/div/div[2]/div[3]/div[{}]/div/div[1]/a'.format(artwork_counter)
                    xpath_artist_name = '//*[@id="root"]/div/div/div[2]/div/div[2]/div[3]/div[{}]/div/div[3]/div/div[1]/a/div[2]'.format(artwork_counter)                
                    xpath_collectors_name = '//*[@id="root"]/div/div/div[2]/div/div[2]/div[3]/div[{}]/div/div[3]/div/div[2]/a'.format(artwork_counter)
                             
                    artwork_name = browser.find_element_by_xpath(xpath_artwork_name).text
                    artwork_href = browser.find_element_by_xpath(xpath_artwork_name).get_attribute('href')
                    artist_name = browser.find_element_by_xpath(xpath_artist_name).text
                    
                    try:
                        collector = browser.find_element_by_xpath(xpath_collectors_name).text
                    except:
                        collector ='N/A or Anonymous'
                    
                    df_collector_artist_pairs.loc[counter,"Artwork"] = artwork_name
                    df_collector_artist_pairs.loc[counter,"Artwork Link"] = artwork_href
                    df_collector_artist_pairs.loc[counter,"Artist"] = artist_name
                    df_collector_artist_pairs.loc[counter,"Artist Link"] = artist_link
                    df_collector_artist_pairs.loc[counter,"Collector"] = collector
                    
                    counter+=1
                except:
                    break
                    
        except:
            pass
        
    return df_collector_artist_pairs
        
def main():
    
    #Specify chromedriver path
    p_chromedriver = r"...\chromedriver.exe"
    p_out = r"C:\Users\kylej\Documents\Crypto Art - Superrare"

    df_top_artists = get_top_artists(p_chromedriver)    
    df_top_artists.to_csv(os.path.join(p_out, "top artists_2021-02-20.csv"),index=False)
    
    df_collector_artist_pairs = crawl_artist_profiles(p_chromedriver, p_out, df_top_artists)
    df_collector_artist_pairs.to_csv(os.path.join(p_out, "superrare top artists and collectors_2021-02-20.csv"),index=False)

main()









    

