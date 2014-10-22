#!/usr/bin/python

import requesocks as requests
import hashlib
import json
import db
import re
from bs4 import BeautifulSoup

class MeatError(Exception):
	'''
	A simple exception.
	'''
	def __init__(self, msg):
		self.msg = msg
		
	def __str__(self):
		return repr(self.msg)

class MeatMachine(object):
	'''
	A Class that keeps state information about a Kingdom of Loathing character and can 
	be used to automate performing simple in-game tasks, such as adventuring, crafting, 
	and consuming crafted items.
	'''
	def __init__(self, proxies={'http':'socks5://127.0.0.1:8080'}):
		self.session = requests.session()
		self.session.proxies = proxies
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
			'response':response,
		}
		response = self.session.post(self.serverURL + '/login.php', params=form_data, allow_redirects=True)
		# self.output('login', response.text)
		if 'login' not in response.url:
			self.loggedin = True
			self.update()
		self.session.get(self.serverURL + '/main.php')

	def logout(self):
		'''
		Logs the user out.
		'''
		if self.loggedin:
			logoutURL = self.serverURL + '/logout.php'
			self.session.get(logoutURL)
			self.loggedin = False

	def update(self):
		'''
		Must be logged in before this method is called. Updates current player state.
		'''
		if not self.loggedin:
			raise MeatError("You must log in before calling update")
		payload = {'what':'status', 'for':'MeatMachine by Moot'}
		response = self.session.get(self.serverURL + '/api.php', params=payload)
		# self.output('update', response.text)
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
		will fight any monster it finds there.
		Must be logged in and provided an integer location id for 'where'.
		For a list of valid location IDs, 
		refer to http://kol.coldfront.net/thekolwiki/index.php/Areas_by_Number
		'''
		if not self.loggedin:
			raise MeatError('You must log in before calling adventure()')
		if(self.adventures == 0):
			return False
		payload = {'snarfblat':where}
		response = self.session.get(self.serverURL + '/adventure.php', params=payload)
		
		if 'Adventure Again' in response.text:
			self.update()
			return True
		
		page = BeautifulSoup(response.text)
		# If you can steal, attempt once
		if page.find('input', value='steal') is not None:
			payload = {'action':'steal'}
			response = self.session.post(self.serverURL + '/fight.php', params=payload)
			
		# Two men enter, one man leave
		while True:
			payload = {'action':'attack'}
			response = self.session.post(self.serverURL + '/fight.php', params=payload)
			if 'Adventure Again' in response.text:
				break
		self.update()
		return True

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
			'quantity':quantity,
		}
		response = self.session.post(self.serverURL + '/skills.php', data=form_data)
		soup = BeautifulSoup(response.text)
		effect = soup.find('td', class_='effect')
		if effect is not None:
			return effect.text
		else: 
			return None
		self.update()
		# self.output('skill',response.text)

	def use_item(self, whichitem):
		'''
		Uses item specified by whichitem once
		'''
		if not self.loggedin:
			raise MeatError('Must be logged in')
		item_id = db.get_id(whichitem)
		if item_id == None:
			raise MeatError('Invalid item name: %s' % whichitem)
		form_data = {
			'pwd': self.pwd,
			'which':3,
			'whichitem':item_id,
			'ajax':1,
			'_':1392657210613,
		}
		response = self.session.get(self.serverURL + '/inv_use.php', params=form_data)
		self.update()
		soup = BeautifulSoup(response.text)
		effect = soup.find('td', class_='effect')
		if effect is not None:
			return effect.text
		else: 
			return None
		# self.output('useitem', response.text)

	def consume(self, kind, what, quantity=1):
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
			'whichitem': item_id,
		}
		if kind is 'food':
			response = self.session.post(self.serverURL + '/inv_eat.php', params=form_data)
		elif kind is 'booze':
			response = self.session.post(self.serverURL + '/inv_booze.php', params=form_data)
		else:
			raise MeatError('kind must be either food or booze, kind: %s ' % kind)
		# self.output('consume', response.text)
		self.update()
		if "You don't have the item you're trying to use" in response.text or "You're too full to eat that" in response.text:
			return False
		else:
			return True

	def use_still(self, what):
		'''
		Will go to the sneaky dude guild and use Nash Crosby's still to
		improve a booze item or ingredient. What is the un-upgraded item name.

		'''
		if not self.loggedin:
			raise MeatError('Must be logged in')
		
		form_data = {
			'whichshop':'still',
		}
		response = self.session.get(self.serverURL + '/shop.php', params=form_data)
		soup = BeautifulSoup(response.text)
		what = db.upgrades[what]
		if what is None:
			raise MeatError('Item {} not found'.format(what))
		for row in soup('input', value='Improve'):
			if what in row.parent.parent.find('b').string:
				whichrow = re.search('whichrow=(.+?)&', row.attrs['rel']).group(1)
				break
		else:
			return soup.text
		
		form_data['action'] = 'buyitem'
		form_data['quantity'] = 1
		form_data['whichrow'] =  whichrow
		form_data['pwd'] = self.pwd
		
		response = self.session.get(self.serverURL + '/shop.php', params=form_data)
		self.update()
		soup = BeautifulSoup(response.text)
		effect = soup.find('td', class_='effect')
		if effect is not None:
			return effect.text
		else:
			return None
		# self.output('still', response.text)

	def craft(self, kind, what, quantity=1):
		'''
		Will attempt to craft the type of item specified by the param 'kind'. 
		'kind' should be 'cocktail' to craft a booze item.
		'''
		if not self.loggedin:
			raise MeatError('Must be logged in')
		if not isinstance(quantity, int):
			raise MeatError('Quantity must be an integer, type(quantity): %s' % type(quantity))
		if kind == 'cocktail':
			cocktail = db.get_drink(what)
		if not self.can_craft(what):
			return False
		form_data = {
				'mode':kind,
				'pwd': self.pwd,
				'action':'craft',
				'qty':quantity,
		}
		parts = cocktail.parts()
		if isinstance(parts[0], db.drink):
			if self.inv_qty(parts[0].id) > 0:
				form_data['a'] = parts[0].id
				form_data['b'] = parts[1]
			else:
				form_data['steps[]'] = [ str(parts[0].parts()).replace(" ","")[1:len(str(parts[0].parts()))-2], str(parts[0].id)+ ","+ str(parts[1])]
		else:
			form_data['a'] = parts[0]
			form_data['b'] = parts[1]
		response = self.session.post(self.serverURL + '/craft.php', params=form_data)
		# self.output('craft', response.text)
		return "You acquire" in response.text

	def can_craft(self, item_name):
		'''
		Returns True if you have the parts to brew this booze item
		'''
		parts_list = db.get_parts(item_name)
		craftable = True
		if len(parts_list) == 0:
			craftable = False
		if len(parts_list) == 4:
			parts_list = parts_list[2:]
		for part in parts_list:
			if self.inv_qty(part) == 0:
				craftable = False
		return craftable

	def output(self, filename, text):
		with open(filename + '.out', 'w') as output:
			output.write(text)

	def has_adventures(self):
		return self.adventures > 0

	def inv_qty(self, item_name):
		'''
		Takes an item name or item id and returns the quantity in your inventory
		'''
		if isinstance(item_name, str):
			key = unicode(db.get_id(item_name))
		elif isinstance(item_name, int):
			key = unicode(item_name)
		elif isinstance(item_name, unicode):
			key = item_name
		if key in self.inventory:
			return int(self.inventory[key])
		else:
			return 0

	def get_inv(self):
		'''
		Prints a mapping of each item in your inventory to its quantity
		'''
		return [(db.get_name(key), self.inv_qty(key)) for key in self.inventory if db.get_name(key) is not None]

	def print_parts(self, item_name):
		'''
		Prints list of items and the inventory quantity for the cocktail specified by item_name
		'''
		print('{}\n------------'.format(item_name))
		for item in db.get_parts(item_name):
			print('{}: {}'.format(db.get_name(item),self.inv_qty(item)))
		print('')
