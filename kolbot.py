#!/bin/python
import re, requests, hashlib, urllib, urllib2, cookielib
from bs4 import BeautifulSoup
from sys import argv


class UrlError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)

def login(s):
	r = s.get('http://www.kingdomofloathing.com')

	loginUrlPattern = re.compile(r'^(.*)login\.php\?loginid=([0-9a-f]+)')
	serverMatch = loginUrlPattern.search(r.url)
	if serverMatch:
		serverURL = serverMatch.group(1)
		print 'serverURL:', serverURL
	else:
		raise UrlError('Error getting serverURL')

	loginChallengePattern = re.compile(r'name="?challenge"?\s+value="?([0-9a-f]+)"?')
	challengeMatch = loginChallengePattern.search(r.text)
	if challengeMatch:
		challenge = challengeMatch.group(1)
		print 'challenge:',challenge
	else:
		raise UrlError('No match to challenge pattern')

	loginID = serverURL[51:]
	
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
	login(s)

main()