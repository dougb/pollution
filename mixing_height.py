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

mixing_height_url = "http://forecast.weather.gov/MapClick.php?w0=t&w3=sfcwind&w10=mhgt&AheadHour=0&Submit=Submit&&FcstType=graphical&site=all&menu=1&textField1=%f&textField2=%f"


filename = "mixing_height_%d.html"

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

def computeTime(month_str,day,hour,meridiem):
    mon = month_map[month_str]
    if meridiem == "pm" and hour != 12:
        hour += 12
    elif meridiem == "am" and hour == 12:
        hour = 0

    now = time.localtime()

    if now.tm_mon == 12 and mon == 1:
        year = now.tm_year + 1
    else:
        year = now.tm_year

    ts = int(time.mktime([year,mon,day,hour,0,0,0,0,0]))

    print "ts:%d (%s)" % (ts, time.localtime(ts))

    return ts


# Main
num_points = 1

grid_points = genGrid(40.148688, -80.332527, 40.717326,-79.596443, num_points)

for i in range(len(grid_points)):
    lat = grid_points[i]['lat']
    lon = grid_points[i]['lon']
    data_ts = int(time.time())
    url = mixing_height_url % (lat,lon)
    print "Fetching url:%s" % (url)
    html_data = fetchUrl(url,filename % (i))
    soup = bs4.BeautifulSoup(html_data,"html.parser")


    weather_data = []
    root_data = { "lat":lat, "lon":lon, "ts":data_ts, "data": weather_data }

    for mp in soup.find_all("map"):
        for area in mp.find_all("area"):
            mouse_over = area.attrs['onmouseover']
            print "MouseOver:%s" % (mouse_over)
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

    print json.dumps(root_data)
                

