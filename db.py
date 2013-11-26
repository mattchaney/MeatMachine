#!/usr/bin/python
from drink import drink

items = {
	# Food
	'insanely spicy bean burrito':316,
	'peach pie':2769,
	# Garnish Components
	'olive':245,
	'strawberry':786,
	'magical ice cubes':1008,
	'coconut shell':1007,
	'cocktail onion':1560,
	'raspberry':1561,
	# Booze Components
	'bottle of gin':237,
	'bottle of vodka':238,
	'bottle of whiskey':328,
	'bottle of rum':787,
	'bottle of tequila':1004,
	'boxed wine':1005,
	'bottle of domesticated turkey':1551,
	'bottle of definit':1552,
	'bottle of calcutta emerald':1553,
	'boxed champagne':1556,
	# Finished Drinks
	'pink pony':684,
	'perpendicular hula':1016,
	'vodka gibson':1569,
	'gibson':1570,
	'parisian cathouse':1571,
	'rabbit punch':1572,
	'vodka stratocaster':1581,
	'neuromancer':1582,
	'prussian cathouse':1583,
	'mae west':1584
}

skills = {
	'disco nap':5007,
	'advanced cocktailcrafting':5014,
	'disco fever':5009,
	'disco leer':5039,
}

drinks = {
	# Premium Cocktails
	'gibson': drink('gibson',1570,1553,1560),
	'rabbit punch':drink('rabbit punch',1572,1551,1561),
	'parisian cathouse':drink('parisian cathouse',1571,1556,1561),
	'vodka gibson':drink('vodka gibson',1569,1552,1560),
	# Extra-Fruity Girl Drinks
	'mae west':drink('mae west',1584,lambda:drinks['rabbit punch'],1008),
	'prussian cathouse':drink('prussian cathouse',1583,lambda:drinks['parisian cathouse'],1008),
	'neuromancer':drink('neuromancer',1582,lambda:drinks['gibson'],1007),
	'vodka stratocaster':drink('vodka stratocaster',1581,lambda:drinks['vodka gibson'],1007),
}

def get_id(name):
		'''
		Takes an item name and returns its id number. Returns None if 
		there is no known item called 'name'
		'''
		if name in items:
			return items[name]
		elif name in skills:
			return skills[name]
		else:
			return None

def get_drink(name):
	'''
	Returns a drink object with the given name, if one is known
	'''
	if name in drinks:
		return drinks[name]
	else:
		return None

def get_all_drinks():
	'''
	Returns a dict of all the drinks
	'''
	return drinks

def get_parts(name):
	'''
	Returns a list containing the parts required to craft the item
	specified by name. A list of length 2 indicates a simple object.
	A list of length 4 indicates a multi-step creation process: the 
	first 2 items combine to create the 3rd, which combines with the 
	4th to create the finished item.
	'''
	cocktail = get_drink(name)
	parts = cocktail.parts()
	parts_list = []
	if isinstance(parts[0],drink):
		parts_list.extend([part for part in parts[0].parts()])
		parts_list.append(parts[0].id)
	else:
		parts_list.append(parts[0])
	parts_list.append(parts[1])
	return parts_list
