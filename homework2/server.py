from flask import Flask, request, make_response
import os
import hmac, hashlib
import base64
import sys

app = Flask(__name__)

cookie_name = "LoginCookie"

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '42'

SECRET = b'asdasdasdkldasld1312312312'

def is_admin(username, password):
	return username == ADMIN_USERNAME and \
		password == ADMIN_PASSWORD

def prepare_data(login_form):
	username = login_form['username'].strip()
	password = login_form['password'].strip()
	return username, password

def make_signature(msg):
	signature = hmac.new(
		SECRET,
		msg=bytes(msg, 'utf-8'),
		digestmod=hashlib.sha256
	).hexdigest().upper()
	return signature

def base64_encode(message):
	message_bytes = message.encode('utf-8')
	base64_bytes = base64.b64encode(message_bytes)
	return base64_bytes

def base64_decode(base64_message):
	message_bytes = base64.b64decode(base64_message)
	message = message_bytes.decode('utf-8')
	return message

def make_cookie_text(username, password, user_group):
	cookie_data = '%s,32131231,com402,hw2,ex2,%s' % (username, user_group)
	signature = make_signature(cookie_data)
	cookie_data = cookie_data + f',{signature}'
	#cookie_data = base64_encode(cookie_data)
	return cookie_data

@app.route("/login",methods=['POST'])
def login():
	username, password = prepare_data(request.form)
	user_group = 'admin' if is_admin(username, password) else 'user'
	cookie_text = base64_encode(make_cookie_text(username, password, user_group))

	response = make_response()
	response.set_cookie(cookie_name, cookie_text)
	return response

@app.route("/auth",methods=['GET'])
def auth():
	statusCode = 0
	response = make_response()
	loginCookie = request.cookies.get(cookie_name)
	if loginCookie == None:
		statusCode = 403
	else:
		loginCookie = base64_decode(loginCookie)
		
		tokens = loginCookie.split(',')
		cookie_signature = tokens[-1]
		no_hmac_cookie = ','.join(tokens[:-1])
		message_signature = make_signature(no_hmac_cookie)

		if cookie_signature != message_signature:
			statusCode = 403
		else:
			userGroup = tokens[-2].strip()
			if userGroup == 'admin':
				statusCode = 200
			else:
				statusCode = 201
	return response, statusCode

if __name__ == '__main__':
	app.run()
