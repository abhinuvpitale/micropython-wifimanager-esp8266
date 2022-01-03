"""
 Implements a simple HTTP/1.0 Server

"""

import socket
import network
import os

# Wifi File Name
WIFI_FILE_NAME = "networks.data"
CURR_WIFI_FILE_NAME = "current_networks.data"

# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080

# defining Wifi errors
INCOMPLETE_REQUEST = 1
NULL_REQUEST = 2

# defining request types
INDEX = 0
WIFI = 1
WIFI_ERROR = 2
NULL_REQUEST_ERROR = 8
OTHER_ERROR = 8
FILE_ERROR = 9

def try_connection():
    """Try connecting to a saved wifi network"""
    CONNECTED = False
    sta_if = None

    # Check if the current network file works
    if CURR_WIFI_FILE_NAME in os.listdir():
        with open(CURR_WIFI_FILE_NAME) as f:
            data = f.readlines()
            data = data.split()
            if len(data) > 0:
                # only read the first line
                (curr_uid, curr_pwd, status) = decode_uid_pwd_from_line(data[0])
                if status:
                    sta_if = do_connect(curr_uid, curr_pwd)
                    print("Connected to {} : {}".format(curr_uid, sta_if.ifconfig()))
                    CONNECTED = True
                else:
                    print("Unable to connect from {}".format(CURR_WIFI_FILE_NAME))
            else:
                print("Empty {}, trying to read from {}".format(CURR_WIFI_FILE_NAME, WIFI_FILE_NAME))
    else:
        print("File {} doesnt exist".format(CURR_WIFI_FILE_NAME))

    # Iterate through the other list of networks
    if not CONNECTED and WIFI_FILE_NAME in os.listdir():
        with open(WIFI_FILE_NAME) as f:
            data = f.readlines()
            if len(data) > 0:
                for line in data:
                    (curr_uid, curr_pwd, status) = decode_uid_pwd_from_line(line)
                    if status:
                        sta_if = do_connect(curr_uid, curr_pwd)
                        print("Connected to {} : {}".format(curr_uid, sta_if.ifconfig()))
                        CONNECTED = True
                        try:
                            with open(CURR_WIFI_FILE_NAME, 'w+') as f:
                                f.write("{}::{}".format(curr_uid, curr_pwd))
                        except:
                            print("Unable to write to {}".format(CURR_WIFI_FILE_NAME))
                        break
                    else:
                        print("Unable to connect from {}".format(WIFI_FILE_NAME))
            else:
                print("Empty {}, please connect to AP to continue".format(WIFI_FILE_NAME))
    else:
        print("File {} doesnt exist".format(WIFI_FILE_NAME))

    return (CONNECTED, sta_if)

# Define a method to connect to a WiFi
def do_connect(ssid, passwd):
   '''
   Constructor - WLAN
   Create a WLAN network interface object. 
   Supported interfaces are 
   1. network.STA_IF (station aka client, 
   connects to upstream WiFi access points)
   2. network.AP_IF (access point, allows 
   other WiFi clients to connect)
   '''
   sta_if = network.WLAN(network.STA_IF)
   '''
   Method - isconnected()
   1. In case of STA mode, returns True if 
   connected to a WiFi access point and 
   has a valid IP address. 
   2. In AP mode returns True when a 
   station is connected. 
   Returns False otherwise.
   '''
   if not sta_if.isconnected():
     print('connecting to network {}'.format(ssid))
     '''
     Method - active()
     Activate (“up”) or deactivate (“down”) 
     nwk interface, 
     if boolean argument is passed. 
     Otherwise, query current state 
     if no argument is provided. 
     '''
     sta_if.active(True)
     '''
     Method - connect()
     Activate (“up”) or deactivate (“down”) 
     nwk interface, 
     if boolean argument is passed. 
     Otherwise, query current state 
     if no argument is provided. 
     '''
     sta_if.connect(ssid, passwd)
     """TODO: Change this infinite time loop to finite one"""
     while not sta_if.isconnected():
       sta_if.active(True)
       print("Connecting..")
       pass
   '''
   Method - ifconfig()
   Get/set IP-level network interface parameters:
   IP address, subnet mask, gateway and DNS server. 
   When called with no arguments, this method 
   returns a 4-tuple with the above information.
   '''
   return sta_if

def decode_uid_pwd_from_line(line):
    """
    Decode Uid and Pwd from single line in file
    returns uid, pwd and status 
    """
    data = line.split("::")
    if len(data) > 1:
        return (data[0], data[1], True)
    else:
        return (None, None, False)

def encode_uid_pwd(uid, pwd):
    """
    Decode Uid and Pwd from single line in file
    returns uid, pwd and status 
    """
    return "{}::{}".format(uid, pwd)

def get_network_from_request(request):
    uid=""
    pwd=""
    request = request.split("\r\n")
    for line in request:
        if len(line) > 3 and line[0:3] == "uid":
            uid = line[4:]
        if len(line) > 3 and line[0:3] == "pwd":
            pwd = line[4:]
    
    
    return(uid, pwd)
            
def handle_request(request):
    """Handles the HTTP request."""
    filename = ""
    errornum = 0
    request_type = None

    if len(request) != 0:
        headers = request.split('\n')
        filename = headers[0].split()[1]

    
    if filename == '/':
        filename = 'index.html'
        request_type = INDEX

    elif filename == "/wifi":
        if len(request) > 0:
            print("Handling new WiFi : {}".format(request[-2]))
            filename = "wifi.html"
            request_type = WIFI
        else:
            print("Incomplete Request")
            filename = "error.html"
            errornum = INCOMPLETE_REQUEST
            request_type = WIFI_ERROR
    elif filename == "":
        errornum = NULL_REQUEST_ERROR
        request_type = NULL_REQUEST
        filename = "error.html"
    else:
        filename = "error.html"
        request_type = NULL_REQUEST_ERROR
        errornum = OTHER_ERROR
        
    try:
        fin = open(filename)
        content = fin.read()
        fin.close()

        response = 'HTTP/1.0 200 OK\n\n' + content
        if errornum != 0:
            response = response + errornum
    except:
        # Catch Other Rando Queries
        response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'
        request_type = FILE_ERROR

    return response, request_type

def start_server(addr):
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(addr)
    #server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(1)
    print('Listening on port %s ...' % SERVER_PORT)
    return server_socket

def check_server(server_socket):
    # Wait for client connections
    client_connection, client_address = server_socket.accept()

    # Get the client request
    request = client_connection.recv(4096).decode()
    # Its weird, so apparently we first read the headers and then the body 
    # of the request, hence we need to read twice to get the complete content. 
    if request and len(request) > 4 and request[0:4] == "POST":
        request1 = client_connection.recv(4096).decode()
        request = request + request1
    print(request)

    # Return an HTTP response
    response, request_type = handle_request(request)
    print("Response: {}".format(response))

    return (client_connection, request, response, request_type)

def update_server(client_connection, response):
    client_connection.sendall(response.encode())

    # Close connection
    client_connection.close()
    return None

def close_server(server_socket):
    # Close socket
    server_socket.close()