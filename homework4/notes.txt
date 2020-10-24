In order to run a shell on client and the mitm respectivelly:

    docker exec -it client /bin/sh 
    docker exec -it mitm /bin/sh 

Set MITM as default gateway on client (can use DNAT on the real default gateway to route traffic through MITM):
    ip route del
    ip route add default via <mitm-IP> dev eth0 

Run on host to get name of container network interface:
    docker exec -it <container-name> cat /sys/class/net/eth0/iflink # place value in grep
    ip ad | grep <obtained-value>

Enable ip forwarding for IPv4 on MITM:
    sysctl -w net.ipv4.ip_forward=1

Enable NAT on MITM:
    iptables -A FORWARD -i eth0 -j ACCEPT
    iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

Route the traffic to the Queue on MITM:
    iptables -D FORWARD -i eth0 -j ACCEPT
    iptables -A FORWARD -j NFQUEUE --queue-num 1



Exercise 2
----------
First byte (Byte 0) of TLS Record Protocol is higher TLS protocol (22 is HANDSHAKE where ClientHello is done).
Fourth and fifth bytes (Bytes 3 and 4) are length of data (exluding the header itself).

    Handshake Protocol format (higher layer stacked after record layer (record layer only 5 bytes))

    First byte is type (Client Hello is 1). Next 3 bytes are handshake message length.

    Handshake message start with 2 bytes for TLS version, then 32 bytes for random number,
    then comes 1 byte for session IDs length. Then each session ID, the size of one should be 4 bytes.
    After that comes CipherSuites (first 2 bytes are length and each 2 next bytes are for 1 cipherId).
    TLS_RSA_WITH_AES_256_CBC_SHA - 0x0035.
    This cipher suite should be replaced with
    TLS_RSA_WITH_AES_128_CBC_SHA - 0x002F.



Exercise 3
----------

B: Self signed cerificate
-------------------------
Generate key using:

    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt

Common name should be server (has something to do because the server is in Docker container).
The generated keys is in /etc/ssl/private/nginx-selfsigned.key and certificate is in /etc/ssl/certs/nginx-selfsigned.crt.
Copy these file into folder certs into server (Docker file is setup to copy them on proper location in container aferwards).
Make yourself the owner of .key file, otherwise you nor Docker will be able to read it.
Seems it is enough to add "ssl on" and key and certificate in conf file in order for HTTPS to work properly.

C: Signed certificate
---------------------
Run 

    openssl genrsa -out request.key 2048
    openssl req -new -key request.key -out request.csr

Common name should still be server.
Place csr file next to docker-compose.yml and then start the container, it has a program that should generate a
certificate (.crt) out of the request file (.csr). Place given files into server/certs and Dockerfile should do the rest.
default.conf should be updated accordingly, but it is already done here.
Check certificate to see who is CA, it should be verifier (don't name anything about your organisation verifier to avoid confusion).


D: Add HSTS
-----------
HSTS is enabled by adding 
    add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
to configuration part of HTTPS server.