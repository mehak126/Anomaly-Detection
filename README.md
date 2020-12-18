# Anomaly Detection in Network Data

COD310 Mini Project, IIT Delhi

**Guide to Programs**

The project consists of 4 files. 
1 client file and 3 gen files.
The client is the node that is receiving the information from the other 3 nodes which are generating them.
This is made to replicate a central node which processes data received from sensors.
Initially generated data points are received and clusters are formed by the client node.
This imitates normal conditions for several days sensed by the above sensors.
Finally, new points are added to be assessed by the client, and are classified as normal/anomalous.

Kindly change the IPs of the nodes as required when trying to run the code. These IPs can be found in lines 48-58 in the client.py file.

The 4 files can be run from a single system as well. If not using raspberry pi's kindly comment out lines 7, 270-278, 283-284, 339-340 in the client.py file.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Guide to Raspberry Pi
Setup:
Install the Raspbian Operating System in a formatted SD card with the help of NOOBS. Follow steps from - https://projects.raspberrypi.org/en/projects/raspberry-pi-getting-started/2

Enabling SSH:
Create an empty file in the BOOT partition of the SD card and name it ssh (without any extension).

Connecting to WiFi:
Create a file ‘wpa_supplicant.conf’ in the BOOT partition and add the text
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
    ssid="SSID"
    psk="PASSWORD"
}
Where “SSID” is the name of the connection and “PASSWORD” is the  password. (source- https://caffinc.github.io/2016/12/raspberry-pi-3-headless/)

For this project, we have used a hotspot with the following properties:
    ssid="Siddhant"
    psk="siddhant"
    
On booting the pi will now be connected to the network with the name and password specified in the .conf file.

Establishing an SSH connection to the pi:
Connect to the same wifi as the pi and use the command “ping raspberrypi.local” to get the ip address of the raspberry pi. SSH into the pi by typing the command “ssh pi@<ip_address>” where <ip_address> is the ip of the pi obtained earlier.

Transferring files:
Transfer files to the pi using SCP. ( https://kb.iu.edu/d/agye )

--------------------------------------------------------------------------------------------------------------------------------------
