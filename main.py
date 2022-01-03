import socket
import os

import wifiManager


# Try connecting to saved wifi
CONNECTED, sta_if = wifiManager.try_connection()

if CONNECTED:
    print("Using Saved Wifi Network")
    while True:
        # your code goes here!
        pass
else:     
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    # start connection
    server_socket = wifiManager.start_server(addr)

    while True:
        # Check the Server for Requests
        client_connection, request, response, request_type = wifiManager.check_server(server_socket)
        # By the end of this step you already have the request and response

        # Update the file
        if request_type == wifiManager.WIFI:
            uid, pwd = wifiManager.get_network_from_request(request)
            if len(uid) > 0 and len(pwd) > 0:
                new_network = wifiManager.encode_uid_pwd(uid, pwd)
                try:
                    with open(wifiManager.WIFI_FILE_NAME, 'a+') as f:
                        f.write(new_network)
                    response = response + uid
                except:
                    print("Unable to Open File!!")
            else:
                pass



        # Update the page
        wifiManager.update_server(client_connection, response)

