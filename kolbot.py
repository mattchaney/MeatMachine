#!/bin/python
import re, requests, hashlib, urllib, urllib2, cookielib
from bs4 import BeautifulSoup

auth = open('auth').read()

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
	
	userName = 'PoorOldMoot'
	pwdHash = hashlib.md5(auth).hexdigest()
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
	s = requests.Session()
	s.auth = ('PoorOldMoot', auth)
	login(s)
	scrounge(s)

main()