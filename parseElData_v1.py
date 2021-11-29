#!/usr/bin/python3
# Get current energy price and post data to MQTT broker, designed to run every hour
# In my case I run this via crontab and data used by Homeassistant


import json
import re
import datetime
import time
import requests
import paho.mqtt.client as mqtt

broker_address="192.168.x.x"
broker_port=1885 #Default 1883
client = mqtt.Client()
client.username_pw_set(username="username", password="password")   #Add user/passw
client.connect(broker_address,broker_port, 60)

output_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
url_date = datetime.datetime.now().strftime("%Y-%m-%d")
updated_date = ' '.join(output_date.split(':')[:-2])


def datarequest():
    r = requests.get('https://www.vattenfall.se/api/price/spot/pricearea/'+ url_date + '/' + url_date + '/SN3')      #SN3 defines the zone and is the only one tested, but following will probably work /SE1	/SE2 /SE3 /SE4 /FI/DK1 /DK2
    rdata = r.json()
    #print(rdata)
    with open('eldata.json', 'w') as outfile:
        json.dump(rdata, outfile)

def parse(found):
    while(found == False):
        try:
            with open('eldata.json') as json_file:
                rdata = json.load(json_file)
        except:
            return(found)

        for i in rdata:
            if re.search(updated_date, (i['TimeStamp'])) :
                client.publish("hass/elpris",i["Value"],0,True) #Change topic 
                found = True
                return(found)

        if found == False:
            time.sleep(10)
    return(found)


def main():
    found = False
    try:
        found = parse(found)
        if found == False:
            datarequest()
            found = parse(found)
    except:
        print ("Error, not found")


if __name__ == "__main__":
    main()

