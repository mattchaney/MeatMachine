#!/usr/bin/env python

class drink(object):
	def __init__(self, name, potency, id, a, b):
		self.name = name
		self.potency = potency
		self.id = id
		self.a = a
		self.b = b

	def parts(self):
		'''
		Returns tuple of drink ingredient item id numbers. If it is a multi-layered drink, 
		i.e. mae west is a rabbit punch and magical ice cubes, a drink object representing
		the drink component will be the first item in the tuple.
		'''
		if isinstance(self.a, type(lambda: None)):
			return self.a(), self.b
		elif isinstance(self.b, type(lambda: None)):
			return self.b(), self.a
		else:
			return self.a, self.b