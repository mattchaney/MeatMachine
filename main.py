#!/usr/bin/python
'''
This is a sample main that is used for a Disco Bandit.
'''
import time, random
from MeatMachine import MeatMachine

def main():
	bot = MeatMachine()
	print(time.strftime("%Y/%m/%d"))

	# auth is a text file containining the account password
	# This is so you can automate this bot to run in the background via something like cron, ie
	bot.login('pooroldmoot', open('auth').read())
	if not bot.loggedin:
		print('Failed to log in')
		exit(0)
	print('You are now logged in')
	print('You have %d adventures' % bot.adventures)

	bot.use_skill('advanced cocktailcrafting', 5)

	# Use the still 10 times for whatever booze items you have
	boozes = ['bottle of vodka', 'bottle of gin', 'bottle of whiskey', 'bottle of rum', 'bottle of tequila']
	garnishes = ['strawberry', 'olive']
	for _ in xrange(5):
		item = random_item(bot, boozes)
		bot.use_still(item)
	for _ in xrange(5):
		item = random_item(bot, garnishes)
		bot.use_still(item)

	# Eat some burritos
	bot.consume('food', 'insanely spicy bean burrito', 5)

	# All you can drink!
	if bot.drunk < 19:
		drinks = {'perpendicular hula':4,'pink pony':4, 'vodka stratocaster':4, 'neuromancer':4, 'mae west':4, 'rabbit punch':4, 'prussian cathouse':4, 'vodka gibson':3}
		drink = random_item(bot, drinks.keys())
		while drink is not None and bot.drunk < 20 - drinks[drink] and bot.consume('booze', drink):
			drink = random_item(bot, drinks.keys())
			print('Drank a %s' % drink)

	# Time to go on an adventure!
	print('Starting with %d adventures' % bot.adventures)
	while bot.has_adventures():
		# use these skills every 10 adventures
		if bot.adventures % 10 == 0:
			bot.use_skill('disco fever', 1)
			bot.use_skill('disco leer', 1)
		if bot.hp < 40:
			bot.use_skill('disco nap', 2)
			print('Used disco power nap twice')
		bot.adventure(110)
		if(bot.adventures % 25 == 0):
			print("%d adventures left, current hp: %d" % (bot.adventures, bot.hp))
	print("Logging out. New meat total: %d." % bot.meat)
	bot.logout()

def random_item(bot, items):
	random.shuffle(items)
	for item in items:
		if(bot.inv_qty(item) > 0):
			return item
	return None

main()