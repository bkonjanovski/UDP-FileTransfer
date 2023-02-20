# Implementation of a variant of the Selective Repeat ARQ protocol algorithm for the sender side
import os
import sys
import socket
import struct
from simple_file_checksum import get_checksum

host = "192.168.0.109" # IP address of the receiver
port = 5001 # random port number
MTU = 1512 # Maximum Transmission Unit in bytes
timeout = 0.00007 
header_size = 54 
buffer_size = MTU - header_size 
file_name = sys.argv[1] 
file_size = os.path.getsize(file_name) 
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
udp_socket.settimeout(timeout) 
window_size = 2500 # number of packets to be sent at a time
ack_seqnums = set() 

print("\n Starting file transfer...\n")
file_checksum = get_checksum(file_name, algorithm="MD5") 
udp_socket.sendto(f"{file_checksum}<>{file_size}".encode(), (host, port)) 
print(" Sending file... \n")  
try: # try block for detecting the Ctrl+C keyboard interrupt
    f = open(file_name, "rb") 
    seq_number = 0 
    datagram = [seq_number,  "start_loop"] 
    while datagram[1]: # 
        sent_datagrams = [] 
        for x in range(window_size):
            read_data = f.read(buffer_size)  
            datagram=[seq_number, read_data] # construct datagram using the sequence number and the read data from the file
            if not read_data:	    
                break
            sent_datagrams.append(datagram) 
            seq_number = seq_number + 1 
        while len(sent_datagrams) > 0:
            try:
                received_data = udp_socket.recvfrom(MTU)
                if received_data[0].decode() == "EXT": 
                    print("\n File transfer stopped by receiver")   
                    f.close()
                    udp_socket.close()
                    sys.exit(0) # if on the receiver side Ctrl+C is pressed, stop the file transfer here
                received_seq_num = int(received_data[0].decode())
                if received_seq_num not in ack_seqnums:
                    ack_seqnums.add(received_seq_num)
                    sent_datagrams = [dgram for dgram in sent_datagrams if dgram[0] != received_seq_num] 
            except TimeoutError: 
                for retry_datagram in sent_datagrams:
                    try:
                        udp_socket.sendto(struct.pack('i1458s', retry_datagram[0], retry_datagram[1]), (host, port))
                    except TimeoutError:
                        continue 
    received_ack = False    
    while not received_ack:
        try:
            received_data = udp_socket.recvfrom(MTU)
            if(received_data[0].decode() == f"EOF Received"):
                received_ack = True
        except TimeoutError:
            for x in range(window_size):
                udp_socket.sendto(f"EOF".encode(), (host, port))	    
            print(f" Sending EOF")  # Sends End of File until corresponding ACK is received
    print(f"\n File transfer finished!")    
        
except KeyboardInterrupt:
    for x in range(window_size):
        udp_socket.sendto(f"EXT".encode(), (host, port))  
    print("\n\n File transfer stopped")

f.close() 
udp_socket.close() 
