#!/bin/python
import requests, hashlib, getpass, json
from bs4 import BeautifulSoup

class MeatError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)

class MeatMachine(object):
	def __init__(self):
		self.session = requests.session()

	def login(self):
		# Get user info
		username = raw_input('Username: ')
		password = getpass.getpass()
		self.session.auth = (username, password)
		response = self.session.get('http://www.kingdomofloathing.com')
		# print 'homepage url:', response.url
		page = BeautifulSoup(response.text)
		self.serverURL = response.url
		loginID = self.serverURL[51:]
		challenge = page.find('input', attrs = {'name':'challenge'})['value']
		pwdHash = hashlib.md5(password).hexdigest()
		hashKey = pwdHash + ":" + challenge
		response = hashlib.md5(hashKey).hexdigest()

		form_data = {
			'loggingin':'Yup.',
			'loginname':username,
			'secure':'1',
			'challenge':challenge,
			'response':response
		}
		response = self.session.post('http://www.kingdomofloathing.com/login.php', data=form_data)
		if 'login' in response.url:
			raise MeatError('Couldn\'t connect')
		# print 'response url:', response.url
		
		self.update_status()
		
		output = open('game', 'w')
		output.write(response.text)
		output.close()

	def update_status(self):
		action = {
			'what':'status',
			'for':'MeatMachine by Moot'
		}
		response = self.session.get('http://www.kingdomofloathing.com/api.php', params=action)
		print response.url

		output = open('api', 'w')
		output.write(response.text)
		output.close()

def main():
	moot = MeatMachine()
	moot.login()

main()