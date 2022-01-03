# micropython-wifimanager-esp8266
Simple Wifi Manager for ESP8266 using MicroPython. 

This is a simple program to be used to connect to the Wifi Network of your choice without having to hardcode the details on your ESP8266. 

It initially runs a simple webserver, that running on its AP Wifi Interface. 
Once you connect to it, it lets you specify the name of the Wifi and its password, which are to be saved to the ESP8266. 

Once you do that, this information is saved and can be used the next time the ESP bootsup. 
