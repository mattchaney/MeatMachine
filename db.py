#!/usr/bin/env python

from drink import drink

items = {
	# Food
	'insanely spicy bean burrito':316,
	'peach pie':2769,
	# Garnish Components
	'orange':242,
	'grapefruit':243,
	'olive':245,
	'lemon':332,
	'strawberry':786,
	'coconut shell':1007,
	'magical ice cubes':1008,
	'kumquat':1557,
	'tangerine':1558,
	'cocktail onion':1560,
	'raspberry':1561,
	'kiwi':1562,
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
	'bottle of lieutenant freeman':1554,
	'bottle of jorge sinsonte':1555,
	'boxed champagne':1556,
	# Finished Drinks
	'pink pony':684,
	'margarita':1013,
	'perpendicular hula':1016,
	'calle de miel':1018,
	'tequila sunset':1565,
	'vodka gibson':1569,
	'gibson':1570,
	'parisian cathouse':1571,
	'rabbit punch':1572,
	'caipifruta':1573,
	'teqiwila':1574,
	'tangarita':1577,
	'vodka stratocaster':1581,
	'neuromancer':1582,
	'prussian cathouse':1583,
	'mae west':1584,
	'mon tiki':1585,
	'teqiwila slammer':1586,
	# Potions
	'bag of Cheat-Os':1787,
}
# Init two-way mapping for items
[items.__setitem__(value, key) for (key,value) in items.items()]

skills = {
	'disco nap':5007,
	'advanced cocktailcrafting':5014,
	'disco fever':5009,
	'disco leer':5039,
}

drinks = {
	# Extra-Fruity Girl Drinks
	'mae west':drink('mae west',4,items['mae west'],lambda:drinks['rabbit punch'],items['magical ice cubes']),
	'prussian cathouse':drink('prussian cathouse',4,items['prussian cathouse'],lambda:drinks['parisian cathouse'],items['magical ice cubes']),
	'neuromancer':drink('neuromancer',4,items['neuromancer'],lambda:drinks['gibson'],items['coconut shell']),
	'vodka stratocaster':drink('vodka stratocaster',4,items['vodka stratocaster'],lambda:drinks['vodka gibson'],items['coconut shell']),
	'teqiwila slammer':drink('teqiwila slammer',4,items['teqiwila slammer'],lambda:drinks['teqiwila'],items['coconut shell']),
	'tangarita':drink('tangarita',4,items['tangarita'],lambda:drinks['tequila sunset'],items['magical ice cubes']),
	'mon tiki':drink('mon tiki',4,items['mon tiki'],lambda:drinks['caipifruta'],items['coconut shell']),
	# Premium Cocktails
	'gibson': drink('gibson',3,items['gibson'],items['bottle of calcutta emerald'],items['cocktail onion']),
	'rabbit punch':drink('rabbit punch',3,items['rabbit punch'],items['bottle of domesticated turkey'],items['raspberry']),
	'parisian cathouse':drink('parisian cathouse',3,items['parisian cathouse'],items['boxed champagne'],items['raspberry']),
	'vodka gibson':drink('vodka gibson',3,items['vodka gibson'],items['bottle of definit'],items['cocktail onion']),
	'teqiwila':drink('teqiwila',3,items['teqiwila'],items['kiwi'],items['bottle of jorge sinsonte']),
	'tequila sunset':drink('tequila sunset',3,items['tequila sunset'],items['kiwi'],items['bottle of jorge sinsonte']),
	'caipifruta':drink('caipifruta',3,items['caipifruta'],items['kiwi'],items['bottle of lieutenant freeman']),
	# Fruity Girl Drinks
	'calle de miel':drink('calle de miel',4,items['calle de miel'],items['magical ice cubes'],items['margarita']),
	# Simple Cocktails
	'margarita':drink('margarita',3,items['margarita'],items['lemon'],items['bottle of tequila']),
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

def get_name(id):
	'''
	Takes an item id number (in unicode or integer form) as input and returns the item's name string
	'''
	if isinstance(id, unicode):
		key = int(id)
	elif isinstance(id, int):
		key = id
	else:
		return None
	if key in items:
		return items[key]
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
	parts_list = []
	if cocktail is not None:
		parts = cocktail.parts()
		if isinstance(parts[0],drink):
			parts_list.extend([part for part in parts[0].parts()])
			parts_list.append(parts[0].id)
		else:
			parts_list.append(parts[0])
		parts_list.append(parts[1])
	return parts_list
