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
		self.loggedin = False

	def login(self):
		'''
		Logs the user in after prompting for username and password. 
		Will not echo password to screen. If a connection error occurs a MeatError is raised
		with an appropriate message. 
		This must be called before any other actions can be taken with the bot.
		'''
		if not self.loggedin:
			username = raw_input('Username: ')
			password = getpass.getpass()
			self.session.auth = (username, password)

			self.serverURL = 'http://www.kingdomofloathing.com'
			response = self.session.get(self.serverURL)
			page = BeautifulSoup(response.text)

			loginID = response.url[51:]
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
			loginURL = self.serverURL + '/login.php'
			response = self.session.post(loginURL, data=form_data)

			self.output('login', response.text)
			
			if 'login' in response.url:
				raise MeatError('Couldn\'t connect')
			else:
				self.loggedin = True
				print 'You are now logged in'
				self.update()
		else:
			raise MeatError("Can't log in, you're already logged in")

	def logout(self):
		'''
		Logs the character out
		'''
		if self.loggedin:
			logoutURL = self.serverURL + '/logout.php'
			response = self.session.get(logoutURL)
			self.loggedin = False
			print 'You have logged out'
		else:
			print "You're already logged out"

	def output(self, filename, text):
		output = open(filename, 'w')
		output.write(text)
		output.close()

	def has_adventures(self):
		return self.adventures > 0

	def update(self):
		'''
		Must be logged in before this method is called.
		'''
		if self.loggedin:
			payload = {
				'what':'status',
				'for':'MeatMachine by Moot'
			}
			response = self.session.get('http://www.kingdomofloathing.com/api.php', params=payload)
			data = json.loads(response.text)
			self.pwd = data['pwd']
			self.hp = int(data['hp'])
			self.maxhp = int(data['maxhp'])
			self.mp = int(data['mp'])
			self.meat = int(data['meat'])
			self.adventures = int(data['adventures'])

			payload = {
				'what':'inventory',
				'for':'MeatMachine by Moot'
			}
			response = self.session.get('http://www.kingdomofloathing.com/api.php', params=payload)
			data = json.loads(response.text)
		else:
			raise MeatError("Can't update: You're not logged in")

	def adventure(self, where):
		'''
		Will attempt to go to the location with the id specified in 'where' and
		will kill any monster it finds there.
		Must be logged in and fed an integer location id for 'where'.
		For a list of valid location IDs, 
		refer to http://kol.coldfront.net/thekolwiki/index.php/Areas_by_Number
		'''
		if self.loggedin:
			if(self.adventures > 0):
				if isinstance(where, int):
					snarfblat = where
					adventureURL = self.serverURL + '/adventure.php'
					payload = {'snarfblat':where}
					response = self.session.get(adventureURL, params=payload)
					page = BeautifulSoup(response.text)

					self.output('adventure', response.text)

					# If you can steal, attempt once
					page.find('input', attrs = {'name':'steal'})
					form_data = {'action':'steal'}
					fightURL = self.serverURL + '/fight.php'
					response = self.session.post(fightURL, data=form_data)
					self.output('steal', response.text)
					page = BeautifulSoup(response.text)
					
					# Two men enter, one man leave
					monster_alive = True
					while monster_alive:
						form_data = {'action':'attack'}
						response = self.session.post(fightURL, data=form_data)
						self.output('attack', response.text)
						
						if 'You win the fight!' in response.text:
							monster_alive = False
							break
					self.update()
					print "%d adventures left and current health is %d" % (self.adventures, self.hp)
					

				else:
					raise MeatError('Adventure location must be an integer')
			else:
				print "You're out of adventures"
				self.logout()
		else:
			self.login()
			self.adventure(where)

	def consume(self, what):
		'''
		Will look in player inventory for the target item 'what' and 
		eat or drink it if it's available. Must be fed an integer item id number to work.
		For a list of valid item IDs, 
		refer to http://kol.coldfront.net/thekolwiki/index.php/Items_by_number
		'''
		pass

	def make(self, what):
		'''
		Will attempt to craft the item specified by the item ID
		'''
		pass

def main():
	moot = MeatMachine()
	moot.login()
	for x in range(20):
		moot.adventure(53)
	while moot.has_adventures():
		moot.adventure(260)

	print "You now have %d meat! Huzzah" % moot.meat
	moot.logout()

main()