Polution
====


### Notes from Mark ###
~~~
Hey there, Doug,

You're quite welcome for the pecans. I enjoyed making them almost as I enjoy eating and sharing them. :-) I also really enjoyed meeting you at lunch.

And thank you for your willingness to support the purchase of a few more sensors. That will help me move the project along quite nicely! Please make the check out to my company, "Blue Lens, LLC" at 6437 Landview Rd., Pittsburgh, PA 15217.

The weather information that I use to predict stinky days (though I didn't predict today's massive stink!) comes from this website: http://forecast.weather.gov/MapClick.php?w0=t&w1=td&w2=wc&w3=sfcwind&w3u=1&w4=sky&w5=pop&w6=rh&w7=rain&w13=mhgt&w13u=0&w16u=1&w17u=1&AheadHour=0&Submit=Submit&FcstType=graphical&textField1=40.2923&textField2=-79.8817&site=all&unit=0&dd=&bw= . 

The tabular version (probably easier to scrape) is here: http://forecast.weather.gov/MapClick.php?w0=t&w1=td&w2=wc&w3=sfcwind&w4=sky&w5=pop&w6=rh&w7=rain&w13=mhgt&AheadHour=0&Submit=Submit&&FcstType=digital&textField1=40.2923&textField2=-79.8817&site=all . 

I pay close attention to mixing height and wind direction, with more emphasis put on mixing height. Winds from the S/SE (going towards N/NW) are optimal for stink, it seems. And winds over 4-5mph can easily mess with the predictability of stink. The Smell PGH app/CREATE Lab at CMU can pull EPA sensor data (including wind direction) and I think they scrape it from this obscenely crude PDF source, updated hourly: http://www.achd.net/airqual/DailySummary.PDF . If you want to duplicate their work, I wouldn't stop you, but I could also discuss the possibility of having them let you pull from their scrape. Ultimately I think that your scrapes could help us establish an automated prediction algorithm-- at least a simple/crude one that we could refine over time. If it works well we might be able to hand the code over to the CREATE lab to integrate into their app. We may also learn other things that spark different approaches and/or local high school projects.

In all of this, please don't feel pressure to spend time or money. I'm happy to work collaborate with you as long as you're interested in helping and have the time to spare, and you certainly have some awesome skills that can move me along more quickly (and provide a valuable service to the community), but if you ever get to a point where it is just too much or you need to step away, I totally understand. Whatever you're moved to contribute will be greatly appreciated, and hopefully pave the way for Pittsburgh to meaningfully close the remaining gaps in our air quality efforts.

And we'll have to do lunch again before too too long. I took a very interesting air sample today during the stinky spell and hope to get it tested soon via the ACHD's fancy new mass spectrometer. Rest assured I'll share the results with you and Ryan!

Thanks again for your support in so many dimensions, and happy holidays!

All the best,
Mark

P.S. Nice job getting the Awair devices! Let me know when you set them up and we can hook you into the Slack group.

~~~


## AWAIR ##

[API Docs](http://docs.awair.is/) - copied incase they take it down.

###Devices###

~~~
curl "https://beta-api.awair.is/v1/users/self/devices"
  -H "Authorization: Bearer {access_token}"
~~~

The above command returns JSON structured like this:

~~~
{
    "pagination": {
        "has_next": true,
        "last_id": 2
    },
    "data": [
        {
            "device_id": 1,
            "device_name": "My Desk",
            "room_type": "Office",
            "location_name": "Gangnamgu, Seoul",
            "latitude": 37.4953685163334,
            "longitude": 127.037206648538,
            "owner_type": "admin"
        },
        {
            "device_id": 2,
            "device_name": "Bedroom",
            "room_type": "Home",
            "location_name": "Gwanakgu, Seoul",
            "latitude": 37.444653348662,
            "longitude": 126.913812465993,
            "owner_type": "admin"
        }
    ]
}
~~~

This endpoint retrieves all of your devices in a paginated fashion.

HTTP Request

`GET https://beta-api.awair.is/v1/users/self/devices`

Query Parameters

|Parameter|Default Description|
|---|---|
|limit   30|The maximum number of devices to return at once|
|last_id 1|If included, device list will be fetched from after the last_id|

###Data###

~~~
curl "https://beta-api.awair.is/v1/devices/:device_id/events/15min-avg"
  -H "Authorization: Bearer {access_token}"
~~~

The above command returns JSON structured like this:

~~~
{
    "data": [
        {
            "timestamp": "2016-06-12T03:30:00.000Z",
            "score": 90,
            "index": {
                "temp": 1,
                "humid": 0,
                "co2": 0,
                "voc": 1,
                "dust": 1
            },
            "sensor": {
                "temp": 23.2,
                "humid": 45.3,
                "co2": 600,
                "voc": 324,
                "dust": 11.3
            }
        }
    ],
    "pagination": {
        "has_next": true,
        "next_from": "2016-06-12T03:45:00.000Z"
    }
}
~~~


This endpoint retrieves device’s 15 minute average data.

HTTP Request

`GET https://beta-api.awair.is/v1/devices/:device_id/events/15min-avg`

 You must replace :device_id with your own device id.
Query Parameters

|Parameter|Default Description|
|---|---|
|limit   10000|The maximum number of data points to return at once|
|from    none|Time to fetch data from (ISO8601 timestamp; e.g. 2016-06-12T03:20:45.483Z)|
|to  none    |Time to fetch data to (ISO8601 timestamp; e.g. 2016-06-13T03:20:45.483Z)|


###Errors###

The Awair API uses the following error codes:

|Error Code|Meaning|
|---|---|
|400 Bad Request|One or more of the request parameters are invalid
|401 Unauthorized | Access token is invalid or not permitted to perform the action requested
|422 Unprocessable Entity |The request parameters were valid but could not be completed due to semantic errors
|404 Not Found | No such endpoint exists
|500 Internal Server Error| Something went wrong on server


###ESDR###

https://esdr.cmucreatelab.org/home

email: doug.esdr@dugos.com

Useful Guide: <https://github.com/CMU-CREATE-Lab/esdr/blob/master/HOW_TO.md>


ClientId: MXHTUP
ClientSecret: 2/BrjVTxC23Dl5uuJVjfeniPH8N4kmuqRn9i1jjp

Create Token.
~~~
curl -X POST -H "Content-Type:application/json" https://esdr.cmucreatelab.org/oauth/token -d @auth.json -o token.json
~~~


Purple Air

[Ryan's Purple Air](https://www.purpleair.com/json?show=3723)

