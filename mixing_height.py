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
import math
import json


month_map = { "Janurary":1, "Feburary":2, "March":3,
           "April":4, "May":5, "June":6,"July":7,"August":8,
           "September":9, "October":10, "November":11, "December":12 
           }

months_regex = "|".join(month_map.keys())

short_month_map = { "Jan":1,"Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7,"Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12 }
short_months_regex = "|".join(short_month_map.keys())

mixing_height_url = "http://forecast.weather.gov/MapClick.php?w0=t&w3=sfcwind&w10=mhgt&AheadHour=0&Submit=Submit&&FcstType=graphical&site=all&menu=1&textField1=%f&textField2=%f"


filename = "/tmp/mx/mixing_height_%d.html"

def float_range(start,end, points):
    if points == 1:
        return [ start ]
    else:
        step = math.fabs(start - end) / points
        return [ start + (x * step) for x in range(points)]


def genGrid(upLeftLat,upLeftLon,lowRighLat,lowRightLon, points):
    lats = float_range(40.148688, 40.717326, points) 
    lons = float_range(-80.332527,-79.596443, points)
    return genLatLons(lats,lons)

def genLatLons(lats,lons):
    lat_lons = [ ]
    for lat in lats:
        for lon in lons:
            lat_lons.append({ "lat":lat, "lon":lon } )
    return lat_lons


def fetchUrl(url,cache_filename):
    data = ""
    if os.path.exists(cache_filename) and os.path.getctime(cache_filename) > (time.time() - 3600):
        print "Reading from cache '%s'" % (cache_filename)
        with open(cache_filename,"rb") as f:
            data = f.read()
    else:
        print "Fetching from web %s" % (url)
        f = urllib2.urlopen(url)
        data = f.read()
        f.close()

        print "Creating cache file '%s'" % (cache_filename)
        with  open(cache_filename,"wb") as f:
            f.write(data)
    return data

def computeTime(month_str,day,hour,meridiem,minute=0,second=0,year=None):
    if month_map.has_key(month_str):
        mon = month_map[month_str]
    else:
        mon = short_month_map[month_str]

    if meridiem == "pm" and hour != 12:
        hour += 11
    elif meridiem == "am":
        if hour == 12:
            hour = 0
        else:
            hour -= 1

    if not year:
        now = time.localtime()
        if now.tm_mon == 12 and mon == 1:
            year = now.tm_year + 1
        else:
            year = now.tm_year

    ts = int(time.mktime([year,mon,day,hour,minute,second,0,0,0]))

    return ts

def getLastUpdate(data):
    grp = re.findall("Last Update: (\d+)\:(\d\d) (am|pm) (\w\w\w) (\w\w\w) (\d+), (\d+)",data,flags=re.MULTILINE)
    if grp:
        (hr,min,meridem,tz,mon_str,mday,year) = grp[0]
        return computeTime(mon_str,int(mday),int(hr),meridem,minute=int(min),year=int(year))
    else:
        print "ERROR:Couldn't find Last Updated"
        return -1

def getElevation(data):
    grp = re.findall("Elev. (\d+)",data,flags=re.MULTILINE)
    if grp:
        return int(grp[0])
    else:
        print "Error Can't figure out Elevation!"
        return -1

# Main
num_points = 1

grid_points = genGrid(40.148688, -80.332527, 40.717326,-79.596443, num_points)

with open('data.json', 'aw') as o:

    for i in range(len(grid_points)):
        lat = grid_points[i]['lat']
        lon = grid_points[i]['lon']
        fetch_ts = int(time.time())
        url = mixing_height_url % (lat,lon)
        print "Fetching url:%s" % (url)
        html_data = fetchUrl(url,filename % (i))
        soup = bs4.BeautifulSoup(html_data,"html.parser")

        lastUpdate_ts = getLastUpdate(html_data)
        elevation_ft = getElevation(html_data)

        weather_data = []
        root_data = { "lat":lat, "lon":lon, "fetchTs":fetch_ts,
                      "lastUpdate_ts":lastUpdate_ts, "elevation":elevation_ft,
                      "data": weather_data }

        for mp in soup.find_all("map"):
            for area in mp.find_all("area"):
                mouse_over = area.attrs['onmouseover']
                #print "MouseOver:%s" % (mouse_over)
                match = re.match(".*(%s) (\d+)\D+(\d+)([a|p]m).+Temperature: (\d+) .+Surface Wind: (\w+) (\d+)mph.+Mixing Height: (\d+)ft" % (months_regex), mouse_over )
                if match:
                    month = match.group(1)
                    day = int(match.group(2))
                    hour = int(match.group(3))
                    meridiem = match.group(4)
                    temp_f = int(match.group(5))
                    temp_c = (float(temp_f) - 32.0) * 5.0/9.0 
                    direction = match.group(6)
                    speed = int(match.group(7))
                    mixing_height = int(match.group(8))
                    fts = computeTime(month,day,hour,meridiem)
                    weather_data.append( { "fts":fts, "direction":direction, "speed":speed, 
                                           "temp":temp_f, 
                                           "mixing_ht":mixing_height } )

                
        print >> o, json.dumps(root_data)
        time.sleep(1)
                

