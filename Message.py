

MESSAGE_TYPE = {
0: "Discover",
1: "Offer",
2: "Request",
3: "Ack",
4: "Decline",
5: "Release",
6: "Renew",
7: "List",
}

class Message:

    def __init__(self, messageType, mac, ip, timestamp):
        """
        DHCP Message
        """
        self.messageType = messageType
        self.clientMac = mac
        self.clientIP = ip
        self.timestamp = timestamp
        self.message_str = str(f"{self.messageType}---{self.clientMac}---{self.clientIP}---{self.timestamp}")

    def decodeMessage(self):
        infoSplit = self.message_str.split('---')
        self.messageType = infoSplit[0]
        self.clientMac = infoSplit[1]
        self.clientIP = infoSplit[2]
        self.timestamp = infoSplit[3]

    def encodeMessage(self):
        self.message_str = str(f"{self.messageType}---{self.clientMac}---{self.clientIP}---{self.timestamp}")

