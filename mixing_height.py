#!/usr/bin/env python
import sys
import os
import os.path
import urllib.request
import bs4
import string
import re
import time
import math
import json
import time
import traceback
from rockset import Client, Q, F
from rockset.exception import Error as RocksetError

month_map = { "January":1, "February":2, "March":3,
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

def fetchUrlRetry(url,cache_filename):
    c = 4
    rc = 0
    data = fetchUrl(url,cache_filename)
    while( len(data) == 0 and  rc < c):
        print("WARNING: Failed to fetch '%s' retrying %d" % (url,rc), file=sys.stderr)
        time.sleep(5)
        rc += 1
        data = fetchUrl(url,cache_filename)
    if(len(data) == 0):
        print("ERROR: Failed to fetch '%s' after %d tries, giving up." % (url,c), file=sys.stderr)
    return data


def fetchUrl(url,cache_filename):
    data = ""
    if os.path.exists(cache_filename) and os.path.getctime(cache_filename) > (time.time() - 3000):
        print("Reading from cache '%s'" % (cache_filename))
        with open(cache_filename,"r") as f:
            data = f.read()
    else:
        print("Fetching from web %s" % (url))
        try:
            f = urllib.request.urlopen(url)
            data = f.read().decode('utf-8')
            f.close()
            print("Creating cache file '%s'" % (cache_filename))
            with  open(cache_filename,"w") as f:
                f.write(data)
        except:
            print("ERROR; Request failed for '%s'" % (url), file=sys.stderr)

    return data

def computeTime(month_str,day,hour,meridiem,minute=0,second=0,year=None):
    if month_str in month_map:
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

    ts = int(time.mktime((year,mon,day,hour,minute,second,0,0,0)))

    return ts

def getLastUpdate(data):
    grp = re.findall("Last Update: (\d+)\:(\d\d) (am|pm) (\w\w\w) (\w\w\w) (\d+), (\d+)",data,flags=re.MULTILINE)
    if grp:
        (hr,min,meridem,tz,mon_str,mday,year) = grp[0]
        return computeTime(mon_str,int(mday),int(hr),meridem,minute=int(min),year=int(year))
    else:
        print("ERROR:Couldn't find Last Updated", data)
        return -1

def getElevation(data):
    grp = re.findall("Elev. (\d+)",data,flags=re.MULTILINE)
    if grp:
        return int(grp[0])
    else:
        print("Error Can't figure out Elevation!")
        return -1

def store_data(rset, json):
    count = 0
    fetch_ts  = json['fetchTs']
    while(count < 3):
        try:
            ret = rset.add_docs([root_data])
            return
        except RocksetError as e:
            print("ROCKSET FAILED! RocksetError ts:%d Error:%s" % (fetch_ts,e),file=sys.stderr)
        except AttributeError as ae:
            tb = traceback.format_exc()
            print("ROCKSET FAILED! AttributeError ts:%d Error:%s TB:%s" % (fetch_ts,ae,tb),file=sys.stderr)
        except:
            e = sys.exc_info()[0]
            print("ROCKSET FAILED! Unknown Error ts:%d %s" % (fetch_ts,e),file=sys.stderr)
        count += 1
        print("RETRYING count:%d" % (count))
        time.sleep(10)
    print("ERROR: Failed to write to RockSet!!!",file=sys.stderr)

# Main
num_points = 10

rs = Client()
pit_inversion_data = rs.Collection.retrieve('pit_inversion_data')


if (not os.path.exists("/tmp/mx")):
    print("Creating /tmp/mx")
    os.mkdir("/tmp/mx") # Make sure tmp dir exists.

grid_points = genGrid(40.148688, -80.332527, 40.717326,-79.596443, num_points)

out_filename = time.strftime("%Y/%m/data%Y%m%d.json",time.gmtime())
os.makedirs(os.path.dirname(out_filename), exist_ok=True)


with open(out_filename, 'a') as o:

    for i in range(len(grid_points)):
        lat = grid_points[i]['lat']
        lon = grid_points[i]['lon']
        fetch_ts = int(time.time())
        url = mixing_height_url % (lat,lon)
        print("Fetching url:%s" % (url))
        html_data = fetchUrlRetry(url,filename % (i))
        soup = bs4.BeautifulSoup(html_data,"html.parser")

        lastUpdate_ts = getLastUpdate(html_data)
        elevation_ft = getElevation(html_data)

        weather_data = []
        root_data = { "lat":lat, "lon":lon, "fetchTs":fetch_ts,
                      "lastUpdate_ts":lastUpdate_ts, "elevation":elevation_ft,
                      "data": weather_data, "_id": "%d%f6.4%f6.4" % (fetch_ts,lat,lon) }

        for mp in soup.find_all("map"):
            for area in mp.find_all("area"):
                mouse_over = area.attrs['onmouseover']
                match = re.match(".*(%s) (\d+)\D+(\d+)([a|p]m).+Temperature: (\d+) .+Surface Wind: (\w+) (\d+|\d+G\d+)mph.+Mixing Height: (\d+|N\/A)" % (months_regex), mouse_over )
                if match:
                    month = match.group(1)
                    day = int(match.group(2))
                    hour = int(match.group(3))
                    meridiem = match.group(4)
                    temp_f = int(match.group(5))
                    temp_c = (float(temp_f) - 32.0) * 5.0/9.0 
                    direction = match.group(6)
                    speed = match.group(7) # This has to be string could be 10 or 10G20.
                    mixing_height_raw = match.group(8)
                    if mixing_height_raw == 'N/A':
                        mixing_height = None
                    else:
                        mixing_height = int(mixing_height_raw)
                    fts = computeTime(month,day,hour,meridiem)
                    weather_data.append( { "fts":fts, "direction":direction, "speed":speed, 
                                           "temp":temp_f, 
                                           "mixing_ht":mixing_height } )
                else:
                    print("WARNING: Match failed, `%s`" % (mouse_over), file=sys.stderr)

        print(json.dumps(root_data),file=o)

        store_data(pit_inversion_data, root_data)

        time.sleep(0.75)
