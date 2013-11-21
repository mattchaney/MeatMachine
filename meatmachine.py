#!/usr/bin/python
import requests, hashlib, json, db, drink
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

	def login(self, username, password):
		'''
		Logs the user in. This must be called before any other actions 
		can be taken with the bot.
		'''
		if self.loggedin:
			return
		password = password.strip()
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
		if 'login' not in response.url:
			self.loggedin = True
			self.update()

	def logout(self):
		'''
		Logs the user out.
		'''
		if self.loggedin:
			logoutURL = self.serverURL + '/logout.php'
			response = self.session.get(logoutURL)
			self.loggedin = False

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
			raise MeatError("You must log in before calling update")
		payload = {'what':'status', 'for':'MeatMachine by Moot'}
		response = self.session.get(self.serverURL + '/api.php', params=payload)
		self.output('update', response.text)
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
		self.inventory = json.loads(response.text)

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
			return
		if not isinstance(where, int):
			raise MeatError('Adventure location must be an integer, type(where): %s' % type(where))
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

	def use_skill(self, what, quantity=1):
		'''
		Uses the skill specified by 'what' with an optional quantity (default is 1)
		Must be logged in before and passed an integer ID.
		For a list of valid skill IDs,
		refer to http://kol.coldfront.net/thekolwiki/index.php/Skills_by_number
		'''
		if not self.loggedin:
			raise MeatError('You must log in before calling use_skill()')
		if not isinstance(quantity, int):
			raise MeatError('Quantity must be an integer, type (quantity): %s' % type(quantity))
		if quantity < 1:
			raise MeatError('Can\'t use this skill a negative quantity of times: too meta')
		skill = db.get_id(what)
		form_data = {
			'pwd':self.pwd,
			'action':'Skillz',
			'whichskill':skill,
			'quantity':quantity
		}
		response = self.session.post(self.serverURL + '/skills.php', data=form_data)
		# self.output('skill',response.text)
		self.update()

	def consume(self, type, what, quantity=1):
		'''
		Will look in player inventory for the target item 'which_item' and 
		eat or drink it if it's available.
		'''
		if not self.loggedin:
			raise MeatError('You must log in first')
		if not isinstance(quantity, int):
			raise MeatError('Quantity must be an integer, type(quantity): %s' % type(quantity))
		if quantity < 1:
			raise MeatError('Can\'t use this skill a negative quantity of times')
		
		item_id = db.get_id(what)
		if item_id == None:
			raise MeatError('Invalid item name')
		form_data = {
			'pwd': self.pwd,
			'which': quantity,
			'whichitem': item_id
		}
		if type is 'food':
			response = self.session.post(self.serverURL + '/inv_eat.php', data=form_data)
		elif type is 'booze':
			response = self.session.post(self.serverURL + '/inv_booze.php', data=form_data)
		else:
			raise MeatError('Type must be either food or booze, type: %s ' % type)
		self.output('consume', response.text)
		self.update()
		if "You don't have the item you're trying to use" in response.text or "You're too full to eat that" in response.text:
			return False
		else:
			return True

	def use_still(self, what, quantity=1):
		'''
		Will go to the sneaky dude guild and use Nash Crosby's still to
		improve a booze item or ingredient
		'''
		if not self.loggedin:
			raise MeatError('Must be logged in')
		if not isinstance(quantity, int):
			raise MeatError('Quantity must be of type integer, quantity: %d' % quantity)
		if(quantity < 1):
			raise MeatError('Quantity must be positive, quantity: %d' % quantity)
		item_id = db.get_id(what)
		if item_id == None:
			raise MeatError('Invalid item name: %s' % what)
		form_data = {
			'action':'stillbooze',
			'whichitem':item_id,
			'quantity':quantity
		}
		response = self.session.post(self.serverURL + '/guild.php', data=form_data)
		self.update()
		# self.output('still', response.text)

	def craft(self, type, what):
		'''
		Will attempt to craft the type of item specified by the param 'type'. 
		'type' should be 'cocktail' to craft a booze item.
		'''
		if not self.loggedin:
			raise MeatError('Must be logged in')
		if type == 'cocktail':
			cocktail = db.get_drink(what)

		print cocktail.ingredients()
		# form_data = {
		# 	'mode':type,
		# 	'a':db.get_id(a),
		# 	'b':db.get_id(b)
		# }
		# response = self.session.post(self.serverURL + '/craft', data=form_data)
		# self.output('craft', response.text)

	def inv_qty(self, item_name):
		'''
		Takes an item name and returns the quantity in your inventory
		'''
		key = unicode(db.get_id(item_name))
		if key in self.inventory:
			return int(self.inventory[key])
		else:
			return 0