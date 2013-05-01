#!/bin/python
import requests, hashlib
from bs4 import BeautifulSoup
from sys import argv


class UrlError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)

def login(s):
	r = s.get('http://www.kingdomofloathing.com')
	page = BeautifulSoup(r.text)
	serverURL = r.url
	loginID = serverURL[51:]
	challenge = page.find('input', attrs = {'name':'challenge'})['value']
	userName = s.auth[0]
	pwdHash = hashlib.md5(s.auth[1]).hexdigest()
	hashKey = pwdHash + ":" + challenge
	response = hashlib.md5(hashKey).hexdigest()

	form_data = {
		'loggingin':'Yup.',
		'loginname':userName,
		'secure':'1',
		'challenge':challenge,
		'response':response
	}

	r = s.post('http://www.kingdomofloathing.com/login.php', data=form_data)
	print r.url
	return r

def scrounge(s):
	form_data = {
		'action' : 'Skillz',
		'whichskill' : '5000',
		'quantity': '1',
		'submit':'Use Skill'
	}

def main():
	script, username, password = argv
	s = requests.Session()
	s.auth = (username, password)
	r = login(s)
	output = open('output', 'w')
	output.write(r.text)
main()