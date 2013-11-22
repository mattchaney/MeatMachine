#! /usr/python

class drink(object):
	def __init__(self, id, a, b):
		self.id = id
		self.a = a
		self.b = b

	def ingredients(self):
		'''
		Returns tuple of drink ingredient item id numbers. If it is a multi-layered drink, 
		i.e. mae west is a rabbit punch and magical ice cubes, a tuple within a tuple is 
		returned. Good luck!
		'''
		if isinstance(self.a, type(lambda: None)) and isinstance(self.b, type(lambda: None)):
			# print 'both'
			return self.a().ingredients(), self.b().ingredients()
		elif isinstance(self.a, type(lambda: None)):
			# print 'just a'
			return self.a().ingredients(), self.b
		elif isinstance(self.b, type(lambda: None)):
			# print 'just b'
			return self.a, self.b().ingredients()
		else:
			# print 'neither'
			return self.a, self.b