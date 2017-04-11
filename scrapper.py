#!/usr/bin/env python
# -*- mode:python tab-width:4; indent-tabs-mode:nil; py-indent-offset:4 -*-
import sys
import os
import urllib2
import urllib
import bs4
import string
from dateutil import parser
import datetime

aqi_url = "http://airnow.gov/index.cfm?action=airnow.national_summary"

filename = "aqi_summary.html"

def fetchUrl(url,cache_filename):
    data = ""
    if os.path.exists(cache_filename):
        print "Reading from cache!"
        with open(cache_filename,"rb") as f:
            data = f.read()
    else:
        print "Fetching from web"
        f = urllib2.urlopen(url)
        data = f.read()
        f.close()

        print "Creating cache"
        with  open(cache_filename,"wb") as f:
            f.write(data)
    return data

def parse_table(tbl):
    rows = []
    for tr in tbl.select("tr"):
        rows.append([d.text for d in tr.select("td")])
    return rows




# Main
data = fetchUrl(aqi_url,filename)

soup = bs4.BeautifulSoup(data)

for tbl in soup.find_all("table", class_="TblInvisibleFixed"):
    for st in tbl.find_all("a", class_="stateblock"):
        print "State:",st.text

    for cit in tbl.find_all("a", class_="NtnlSummaryCity"):
        print "City:", cit.text

    for tbl2 in tbl.find_all("table",class_="TblInvisible"):
        for td in tbl2.select("td"):
            print "Data:",string.strip(td.text)
    print "-----------"

# class TblInvisibleFixed
# class NtnlSummaryStateHeader
# class NtnlSummaryCity
    
                
