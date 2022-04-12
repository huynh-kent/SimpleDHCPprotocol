# SimpleDHCPprotocol

Replicates DHCP protocol(Dynamic Host Configuration Protocol) using Socket Programming

Client and Server communicate through UDP Sockets

Server contains a list of records of its range of valid IP addresses for 192.168.45.0/28 
  aka 192.168.45.1-192.168.45.14
The records are stored in memory through SQLite

Implements SQLite3 to store and edit records of IP addresses

Each record contains [ IP address, MAC address, Timestamp, Acked, Record Number ]

Client sends a Discover message

Server offers an IP address 

Client requests the offered IP address

Server acknowledges leasing the IP address to client

Client Receives a menu with options to Renew/Release/Quit

