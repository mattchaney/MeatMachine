#!/usr/bin/python
import requests, hashlib, getpass, json
from BeautifulSoup import BeautifulSoup

class MeatError(Exception):
	def __init__(self, msg):
		self.msg = msg
		
	def __str__(self):
		return repr(self.msg)

class MeatMachine(object):
	def __init__(self):
		self.items = {
			#food
			'insanely spicy bean burrito':316,
			'peach pie':2769,
			#booze components
			'magical ice cubes':1008,
			'coconut shell':1007,
			'cocktail onion':1560,
			'raspberry':1561,
			#booze
			'bottle of domesticated turkey':1551,
			'bottle of definit':1552,
			'bottle of calcutta emerald':1553,
			'boxed champagne':1556,
		}
		self.session = requests.session()
		self.loggedin = False

	def login(self):
		'''
		Logs the user in after prompting for username and password. 
		Will not echo password to screen. If a connection error occurs a MeatError is raised
		with an appropriate message. 
		This must be called before any other actions can be taken with the bot.
		'''
		if self.loggedin:
			return
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
			print 'Couldn\'t connect... for some reason'
		else:
			self.loggedin = True
			print 'You are now logged in'
			self.update()

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
		if not self.loggedin:
			raise MeatError("def update: You must log in before calling update")
		payload = {'what':'status', 'for':'MeatMachine by Moot'}
		response = self.session.get(self.serverURL + '/api.php', params=payload)
		data = json.loads(response.text)
		self.pwd = data['pwd']
		self.hp = int(data['hp'])
		self.maxhp = int(data['maxhp'])
		self.mp = int(data['mp'])
		self.meat = int(data['meat'])
		self.drunk = int(data['drunk'])
		self.adventures = int(data['adventures'])
		payload = {'what':'inventory', 'for':'MeatMachine by Moot'}
		response = self.session.get(self.serverURL + '/api.php', params=payload)
		self.invenvtory = json.loads(response.text)

	def adventure(self, where):
		'''
		Will attempt to go to the location with the id specified in 'where' and
		will kill any monster it finds there.
		Must be logged in and fed an integer location id for 'where'.
		For a list of valid location IDs, 
		refer to http://kol.coldfront.net/thekolwiki/index.php/Areas_by_Number
		'''
		if not self.loggedin:
			raise MeatError('def adventure: You must log in before calling adventure()')
		if(self.adventures == 0):
			print "You're out of adventures"
			return
		if not isinstance(where, int):
			raise MeatError('def adventure: Adventure location must be an integer')

		snarfblat = where
		adventureURL = self.serverURL + '/adventure.php'
		payload = {'snarfblat':where}
		response = self.session.get(adventureURL, params=payload)
		page = BeautifulSoup(response.text)
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
			raise MeatError('def use_skill: You must log in before calling use_skill()')
		if not isinstance(what, int):
			raise MeatError('def use_skill: Skill id must be an integer')
		if quantity < 1:
			raise MeatError('def use_skill: Can\'t use this skill a negative quantity of times: too meta')
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

	def consume(self, type, which_item, how_many=1):
		'''
		Will look in player inventory for the target item 'which_item' and 
		eat or drink it if it's available. Must be fed an integer item id number to work.
		For a list of valid item IDs, 
		refer to http://kol.coldfront.net/thekolwiki/index.php/Items_by_number
		'''
		if not self.loggedin:
			raise MeatError('def consume: You must log in first')
		if not isinstance(which_item, int) or not isinstance(how_many, int):
			raise MeatError('def consume: Parameter how_many and which_item must be of type integer')
		if how_many < 1:
			raise MeatError('def consume: Can\'t use this skill a negative quantity of times')
		form_data = {
			'pwd': self.pwd,
			'which': how_many,
			'whichitem': which_item
		}
		if type is 'food':
			response = self.session.post(self.serverURL + '/inv_eat.php', data=form_data)
		elif type is 'booze':
			response = self.session.post(self.serverURL + '/inv_booze.php', data=form_data)
		else:
			raise MeatError('Type must be either food or booze')
		self.output('consume', response.text)
		self.update()

	def craft(self, what, a, b):
		'''
		Will attempt to craft the type of item specified by the param 'what'. 
		'what' should be 'cocktail' to craft a booze item.
		'''
		# if not self.loggedin:
		# 	raise MeatError('Must be logged in')
		# form_data = {
		# 	'mode':what,
		# 	'a':get_id(a),
		# 	'b':get_id(b)
		# }
		# response = self.session.post(self.serverURL + '/craft', data=form_data)
		# self.output('craft', response.text)

	def get_id(self, item_name):
		return self.items[item_name]
