#!/usr/bin/python
'''
This is a sample main that is used for a Disco Bandit.
'''
import time
import random
import db
import meatmachine

def main():
	bot = meatmachine.MeatMachine()
	print(time.strftime("%Y/%m/%d"))

	# auth is a text file containining the account password
	# This is so you can automate this bot to run in the background via something like cron
	bot.login('pooroldmoot', open('auth').read())
	if not bot.loggedin:
		print('Failed to log in')
		exit(1)
	print('You are now logged in')
	print('You have {} adventures'.format(bot.adventures))

	bot.use_skill('advanced cocktailcrafting', 5)

	# Use the still 10 times for whatever booze items you have
	boozes = ['boxed wine','bottle of vodka', 'bottle of whiskey', 'bottle of gin', 'bottle of tequila']  
	garnishes = ['strawberry', 'olive', 'lemon', 'grapefruit'] # 'orange' is out 
	
	use_still(bot, boozes)
	use_still(bot, garnishes)
	
	# Eat some burritos
	for __ in xrange(5):
		if bot.consume('food', 'insanely spicy bean burrito'):
			print('Ate an insanely spicy bean burrito')		

	# Make some cocktails
	drinks = db.get_all_drinks()
	drinksmap = brew(bot, drinks)

	# All you can drink!
	drink = random_item(bot, drinksmap.keys())
	while drink is not None and bot.drunk < 20 - drinksmap[drink]:
		if bot.consume('booze', drink):
			print('Drank a {}'.format(drink))
		drink = random_item(bot, drinksmap.keys())
			
	# Time to go on an adventure!
	adventure(bot)

	# A nightcap
	[bot.consume('booze', item) for item in drinks if bot.inv_qty(item) > 0]
	bot.update()
	print("Logging out. New meat total: {}".format(bot.meat))
	bot.logout()

def adventure(bot):
	print('Starting with %d adventures' % bot.adventures)
	while bot.has_adventures():
		# use these every 10 adventures
		if bot.adventures % 10 == 0:
			print bot.use_item('bag of Cheat-Os')
			print bot.use_skill('disco fever')
			print bot.use_skill('disco leer')
		if bot.hp < 40:
			print bot.use_skill('disco nap', 2)
		if not bot.adventure(110):
			print('still broken')
			sys.exit(1)
		if(bot.adventures % 25 == 0):
			print("{} adventures left, current hp: {}".format(bot.adventures, bot.hp))

def brew(bot, drinks):
	drinksmap = {}
	for drink in drinks:
		drinksmap[drink] = drinks[drink].potency
		if bot.can_craft(drink):
			while bot.craft('cocktail', drink):
				print("Mixed a {}".format(drink))
	return drinksmap


def use_still(bot, items):
	for __ in xrange(5):
		item = random_item(bot, items)
		if item is None:
			return
		result = bot.use_still(item)
		print result
		if 'Uh Oh' in result:
			return

def random_item(bot, items):
	random.shuffle(items)
	for item in items:
		if bot.inv_qty(item) > 0:
			return item
	return None

def get_item(bot, items):
	for item in items:
		if bot.inv_qty(item) > 0:
			return item
	return None

if __name__ == '__main__':
	main()