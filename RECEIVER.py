# Implementation of a variant of the Selective Repeat protocol algorithm for the receiver side
import sys
import tqdm
import socket
import struct
from simple_file_checksum import get_checksum

host = "0.0.0.0" # receive file transfers from any IP address
port = 5001 # random port number
MTU = 1512 # Maximum Transmission Unit in bytes
file_name = sys.argv[1] 
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
udp_socket.bind((host, port)) 
window_size = 2500 # number of packets to be received at a time
print("\n Waiting for file transfer...\n")
received = udp_socket.recvfrom(MTU)  
address = received[1] 
expected_checksum, file_size = received[0].decode().split("<>") # extract expected checksum of file and the file size  
progress = tqdm.tqdm(range(int(file_size)), f" Receiving {file_name}", unit="B", unit_scale=True,unit_divisor=1000) # this is for the visual progress bar indicator
f = open(file_name, 'wb') 
received_seqnums = set() s
received_datagrams =  [] 
try: # try block for detecting the Ctrl+C keyboard interrupt
    while True:
        received = udp_socket.recvfrom(MTU)
        try:    
            received = struct.unpack('i1458s', received[0]) # deserialize received data
        except:
            if received[0].decode() == "EXT": 
                progress = 0
                print("\n File transfer stopped by sender")
                break
            for x in range(window_size):
                udp_socket.sendto(f"EOF Received".encode(), address) 
            received_datagrams = sorted(received_datagrams, key=lambda datagram: datagram[0])
            for write_datagram in received_datagrams:
                f.write(write_datagram[1])
            break # Send EOF confirmation and end file transfer
        data = received[1] 
        seq_number = received[0] 
        if seq_number not in received_seqnums:
            received_seqnums.add(seq_number)
            if(data.endswith(b'\x00\x00\x00')):
                last_seq_number = received[0]
                last_packet = data.rstrip(b'\x00')
                received = (last_seq_number, last_packet) # if the data ends with \x00 it means that it is the last packet from the file, and that extra padding added by the serialization must be removed
            received_datagrams.append(received)
            if len(received_datagrams) == window_size:
                received_datagrams = sorted(received_datagrams, key=lambda datagram: datagram[0]) # sort received datagrams based on sequence number before writing to file
                for write_datagram in received_datagrams:
                    f.write(write_datagram[1]) 
                received_datagrams =  []
            progress.update(len(data)) # update the visual progress bar indicator
        udp_socket.sendto(f"{seq_number}".encode(), address) # send ACK for specific packet 
        
except KeyboardInterrupt: # handle exception block the Ctrl+C keyboard interrupt
    progress = 0
    for x in range(window_size):
        udp_socket.sendto(f"EXT".encode(), address) # send Exit signal to sender
    print("\n\n File transfer stopped")

progress = 0 
f.close() 
udp_socket.close()

print("\n Verifying file checksum...")
actual_checksum = get_checksum(file_name, algorithm="MD5") 
if(actual_checksum == expected_checksum):
    print("\n File transfer successful!")
else:
    print("\n File transfer error!")

