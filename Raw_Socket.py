#!/usr/bin/python3.5

#import all the required modules
#os module is used for error printing
import socket, sys, os
from struct import * 

#this is the internet checksum function
#summation of 16bits(carry has to be added) and 
#then taking summation's 1's(negate) compliment 
def checksum(msg):
	s=0
	for item in range(0,len(msg),2):
		word = (msg[item]) + ((msg[item+1])<<8)
		s += word
	
	s = s + (s >> 16)
	s = ~s & 0xffff
	return s


try:
	tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

except OSError as errorMessage:
	print("Socket Creation failed with eror code %s and error message:%s"%(errorMessage.errno,errorMessage.strerror))
	sys.exit()
print("RAW TCP Socket Creation Complete")

packet = ''

#Now we have to create the headers
# First is IP Header

source_ip = '192.168.2.1'
destination_ip = '10.110.255.48'

ip_version = 4
ip_ihl = 5
ip_tos = 0
ip_tol = 0
ip_id =  5432
ip_fragoffset = 0 
ip_ttl = 255
ip_proc = socket.IPPROTO_TCP
ip_checksum = 0
ip_sourceaddr = socket.inet_aton(source_ip)
ip_destinationaddr = socket.inet_aton(destination_ip)

ip_ihl_version = (ip_version<<4) + ip_ihl

ip_header = pack('!BBHHHBBH4s4s' , ip_ihl_version, ip_tos, ip_tol, ip_id, ip_fragoffset, 
	ip_ttl, ip_proc, ip_checksum, ip_sourceaddr, ip_destinationaddr)
print("IP Header Creation Complete!")

#we have packed the header according to the IP Header

# Now we will create TCP header

tcp_sourceport = 8888
tcp_destport = 5555
tcp_sequencenum = 5000
tcp_acknumber = 0
tcp_dataoffset = 5
#tcp_reserved = 
tcp_urg = 0 
tcp_ack = 0
tcp_psh = 0
tcp_rst = 0
tcp_syn = 1
tcp_fin = 0
tcp_window = socket.htons(2400)
tcp_checksum = 0
tcp_urgpointer = 0

tcp_offset_reserved = (tcp_dataoffset << 4 ) + 0
tcp_flags = tcp_fin + (tcp_syn<<1) + (tcp_rst<<2) + (tcp_psh<<3) + (tcp_ack<<4) + (tcp_urg<<5)

tcp_header = pack('!HHLLBBHHH' , tcp_sourceport, tcp_destport, tcp_sequencenum, tcp_acknumber, 
	tcp_offset_reserved, tcp_flags,  tcp_window, tcp_checksum, tcp_urgpointer)


user_data = b"Hey There!!!"

#Pseudo Header

source_address = socket.inet_aton(source_ip)
destination_address = socket.inet_aton(destination_ip)
placeholder = 0
protocol = socket.IPPROTO_TCP
tcp_length = len(tcp_header) + len(user_data)

psh = pack('!4s4sBBH' , source_address , destination_address , placeholder , protocol , tcp_length)
psh = psh + tcp_header + user_data

tcp_checksum = checksum(psh)

tcp_header = pack('!HHLLBBH' , tcp_sourceport, tcp_destport, tcp_sequencenum, tcp_acknumber, 
	tcp_offset_reserved, tcp_flags,  tcp_window) + pack('H',tcp_checksum)+ pack('H', tcp_urgpointer)

print("TCP Header Creation Complete!")
packet = ip_header + tcp_header + user_data

for _ in range(10000):
	tcpSocket.sendto(packet, (destination_ip , 0 ))

print("Sending Complete and now closing the TCP RAW Socket")
tcpSocket.close()