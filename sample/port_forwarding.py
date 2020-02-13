import sys
sys.path.append('../')
import speedify
import connectify
import json
import os
import subprocess
import sys
import platform
import time
import ctypes

from speedify import SpeedifyError
import logging

# NETSH requires this to be run as administrator

logging.basicConfig(handlers=[logging.FileHandler('test.log'),logging.StreamHandler(sys.stdout)],format='%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s',  level=logging.INFO)


# netsh, ONLY SUPPORTS TCP FORWARDINGG
#EDIT THIS WITH YOUR PORTS AND IPS
forwarded_ports=[
    { "internet_port":10008, "proto":"tcp","client_port":8080, "client_ip":"192.168.138.102"},
    { "internet_port":999, "proto":"tcp","client_port":8080, "client_ip":"192.168.138.103"}
    ]


# DON'T EDIT BELOW HERE
tcp_ports = []
udp_ports = []
used_internet_ports = []
speedify_client_ip = "10.202.0.2"

if platform.system().lower() != "windows":
    print("Usage: Windows only!")
    sys.exit()
if not ( ctypes.windll.shell32.IsUserAnAdmin() != 0):
    print("Usage: Must be run as admin")
    sys.exit()


speedify.disconnect()
connectify_clients = connectify.clients()

# Remove any old Firewall/port forwarding rules from previous runs
cmd = ["netsh","interface","portproxy","reset"]
try:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True,check=True, timeout=600)
except Exception as e:
    print("problem running netsh: "+ str(e))

    cmd = ["netsh","advfirewall","firewall", "delete","rule",
        "name=Speedify_Port", "dir=in"]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,check=True, timeout=600)
    except Exception as e:
        print("problem running netsh: "+ str(e))
    cmd = ["netsh","advfirewall","firewall", "delete","rule",
        "name=Connectify_Port", "dir=in"]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,check=True, timeout=600)
    except Exception as e:
        print("problem running netsh: "+ str(e))


for rule in forwarded_ports:
    internet_port = rule["internet_port"]
    if internet_port in used_internet_ports:
        print("Error: internet ports must be unique.  Port " + str(internet_port))
    used_internet_ports.append(internet_port)
    client_port = rule["client_port"]
    client_ip = rule["client_ip"]
    client_exists = False
    for cc in connectify_clients:
        if cc["IP"] == client_ip:
            client_exists = True;
            if(cc["StaticIP"] == ""):
                print("Warning: Connectify Hotspot not using a static ip on " + client_ip)
    if not client_exists:
        print("Warning: no such client in Connectify Hotspot: "+ client_ip)
        # go ahead anyway
    proto = rule["proto"]
    if proto == "tcp":
        tcp_ports.append(internet_port)
    if proto == "udp":
        udp_ports.append(internet_port)
    # add the windows firewall port forwarding
    cmd = ["netsh","interface","portproxy","add","v4tov4",
        "listenaddress="+ speedify_client_ip,"listenport=" + str(internet_port),
        "connectaddress=" + str(client_ip), "connectport=" + str(client_port)]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,check=True, timeout=600)
    except Exception as e:
        print("problem running netsh: "+ str(e))
    # make sure the port is open for incoming traffic on the speedify interface
    cmd = ["netsh","advfirewall","firewall", "add","rule", "name=Speedify_Port",
        "dir=in", "action=allow","protocol=TCP", "localport=" + str(internet_port)]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,check=True, timeout=600)
    except Exception as e:
        print("problem running netsh: "+ str(e))

    # open the outgoing firewall port to all communications with connectify client
    cmd = ["netsh","advfirewall","firewall", "add","rule", "name=Connectify_Port",
        "dir=out", "action=allow","protocol=TCP", "localport=" + str(client_port)]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,check=True, timeout=600)
    except Exception as e:
        print("problem running netsh: "+ str(e))

try:
    # actually set the ports in speedify
    speedify.ports(tcp_ports,udp_ports)
    # connect to closest private server
    serverinfo = speedify.connect_private()
    print("Public IP: " + serverinfo["publicIP"][0])
    print("TCP Ports " + str(tcp_ports) )
except SpeedifyError as se:
    print("Problem setting ports: " + str(se))
