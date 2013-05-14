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
			pwdHash = hashlib.md5(password).hexdigest()
			challenge = page.find('input', attrs = {'name':'challenge'})['value']
			hashKey = pwdHash + ":" + challenge
			response = hashlib.md5(hashKey).hexdigest()
			form_data = {
				'loggingin':'Yup.',
				'loginname':username,
				'secure':'1',
				'challenge':challenge,
				'response':response
			}
			response = self.session.post(self.serverURL + '/login.php', data=form_data)
			# self.output('login', response.text)
			if 'login' in response.url:
				raise MeatError('Couldn\'t connect... for some reason')
			else:
				self.loggedin = True
				print 'You are now logged in'
				self.update()
		else:
			return

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
			payload = {'what':'status', 'for':'MeatMachine by Moot'}
			response = self.session.get(self.serverURL + '/api.php', params=payload)
			data = json.loads(response.text)
			self.pwd = data['pwd']
			self.hp = int(data['hp'])
			self.maxhp = int(data['maxhp'])
			self.mp = int(data['mp'])
			self.meat = int(data['meat'])
			self.adventures = int(data['adventures'])
			payload = {'what':'inventory', 'for':'MeatMachine by Moot'}
			response = self.session.get(self.serverURL + '/api.php', params=payload)
			data = json.loads(response.text)
		else:
			raise MeatError("You must log in before calling update")

	def adventure(self, where):
		'''
		Will attempt to go to the location with the id specified in 'where' and
		will kill any monster it finds there.
		Must be logged in and fed an integer location id for 'where'.
		For a list of valid location IDs, 
		refer to http://kol.coldfront.net/thekolwiki/index.php/Areas_by_Number
		'''
		if not self.loggedin:
			raise MeatError('You must log in before calling adventure()')
		if(self.adventures == 0):
			print "You're out of adventures"
			return
		if not isinstance(where, int):
			raise MeatError('Adventure location must be an integer')

		snarfblat = where
		adventureURL = self.serverURL + '/adventure.php'
		payload = {'snarfblat':where}
		response = self.session.get(adventureURL, params=payload)
		page = BeautifulSoup(response.text)
		# If this is a non-combat adventure, just return
		if 'Adventure Again' in response.text:
			self.update()
			return
		# If you can steal, attempt once
		if None != page.find('input', attrs = {'name':'steal'}):
			form_data = {'action':'steal'}
			response = self.session.post(self.serverURL + '/fight.php', data=form_data)
		# Two men enter, one man leave
		monster_alive = True
		while monster_alive:
			form_data = {'action':'attack'}
			response = self.session.post(self.serverURL + '/fight.php', data=form_data)
			if 'Adventure Again' in response.text:
				monster_alive = False
				break
		self.update()
		print "%d adventures left and current health is %d" % (self.adventures, self.hp)

	def use_skill(self, what, quantity=1):
		'''
		Uses the skill specified by 'what' with an optional quantity (default is 1)
		Must be logged in before and passed an integer ID.
		For a list of valid skill IDs,
		refer to http://kol.coldfront.net/thekolwiki/index.php/Skills_by_number
		'''
		if not self.loggedin:
			raise MeatError('You must log in before calling use_skill()')
		if not isinstance(what, int):
			raise MeatError('Skill id must be an integer')
		if quantity < 1:
			raise MeatError('Can\'t use this skill a negative quantity of times: too meta')
		skill = what
		form_data = {
			'pwd':self.pwd,
			'action':'Skillz',
			'whichskill':skill,
			'quantity':quantity
		}
		response = self.session.post(self.serverURL + '/skills.php', data=form_data)
		# self.output('skill',response.text)
		self.update()

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
	# 51 = Menagerie lvl1, 53 = Menagerie lvl2, 110 = icy peak 
	bot = MeatMachine()
	bot.login()
	bot.use_skill(5014, 3) # Advanced Cocktailcrafting
	for x in range(10):
		bot.adventure(51)
	for x in range(15):
		bot.adventure(53)
	while bot.has_adventures():
		if bot.hp < 40:
			bot.use_skill(5011, 2)
			print 'Took 2 Disco Power Naps...'
		bot.adventure(110)
	print "You now have %d meat! Huzzah" % bot.meat
	bot.logout()

main()