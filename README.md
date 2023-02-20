# UDP-FileTransfer
Reliable UDP data transport implementation
 
A command-line tool written and tested in Python3 for Linux.

Tested 3 different ARQ variants: 
 - Stop and Wait ARQ 
 - Go Back N ARQ 
 - Selective Repeat ARQ 
 
Measured and compared these different approaches under harsh emulated network condition. <br> The <b>Selective Repeat ARQ</b> algorithm variant gives the fastest speed results.

1. For the receiver side, install two additional python modules:
    - <b>tqdm</b> – for the progress bar indicator 
    - <b>simple_file_checksum</b> – for calculating the md5 file checksums
   
   Both can be installed with <b>pip</b>.
2. Set the IP address of the receiver in the <b>SENDER.py</b> file

3. Start the <b>RECEIVER.py</b> to wait for incoming file transfers with the first command line argument representing the name of the file you want to receive:
 <i>python RECEIVER.py {name_of_received_file}</i>
 
4. Next, on the sender side run the <b>SENDER.py</b>: <i>python SENDER.py {name_of _file_to_send}</i>

After this, the file transfer will start and on the receiver side there is a progress bar indicator showing the status, file size and time, as well as the average speed per second of the transfer. The transfer can be stopped any time on both the sender or receiver side by pressing Ctrl+C.
<br>When the file transfer finishes, the receiver side will automatically calculate a MD5 checksum and compare it to the expected checksum from the sender and verify the file integrity. It will work for any file size and type.
Tested with a 1GB random binary file generated with the command:
<i>dd if=/dev/urandom of=randomfile bs=8M count=125</i>

For setting emulated delays and losses, tested with the following cases and got the following corresponding time results:

<pre>
 - sudo tc qdisc add dev eth0 root netem rate 100mbps                      - 1min:34sec
 - sudo tc qdisc add dev eth0 root netem rate 100mbps delay 5ms loss 1%    - 2min:2sec
 - sudo tc qdisc add dev eth0 root netem rate 100mbps delay 5ms loss 10%   - 2min:16sec
 - sudo tc qdisc add dev eth0 root netem rate 100mbps delay 50ms loss 10%  - 4min:17sec
 - sudo tc qdisc add dev eth0 root netem rate 100mbps delay 500ms loss 1%  - 20min:58sec
 </pre>
 
