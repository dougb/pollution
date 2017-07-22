#!/usr/bin/env python
# -*- mode:python tab-width:4; indent-tabs-mode:nil; py-indent-offset:4 -*-
import sys
import os
import urllib2
import urllib
import bs4
import string
import re
import time

months = "Janurary|Feburary|March|April|May|June|July|August|September|October|November|December"

mixing_height_url = "http://forecast.weather.gov/MapClick.php?w10=mhgt&AheadHour=0&Submit=Submit&&FcstType=graphical&textField1=40.4237&textField2=-79.8854&site=all&menu=1"

filename = "mixing_height.html"

def fetchUrl(url,cache_filename):
    data = ""
    if os.path.exists(cache_filename) and os.path.getctime(cache_filename) > (time.time() - 3600):
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

# Main
data = fetchUrl(mixing_height_url,filename)

soup = bs4.BeautifulSoup(data,"html.parser")

for mp in soup.find_all("map"):
    for area in mp.find_all("area"):
        mouse_over = area.attrs['onmouseover']

        #  writeText('<b>Sunday, July 23 at  12pm</b><br>Mixing Height: 1900ft')
        mx_ht_match = re.match(".*(%s) (\d+) at\s+(\d+[a|p]m).*Height: (\d+)ft" % (months),mouse_over)
        if mx_ht_match:
            month = mx_ht_match.group(1)
            day = int(mx_ht_match.group(2))
            hour = mx_ht_match.group(3)
            ft = int(mx_ht_match.group(4))
            print "Mixing HT Month:%s Day:%d HR:%s Height:%dft" % (month,day,hour,ft)

