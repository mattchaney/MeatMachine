#!/usr/bin/env python
'''
This is a sample main that is used for a Disco Bandit.
'''
import time, random, db
from meatmachine import MeatMachine

def main():
	bot = MeatMachine()
	print(time.strftime("%Y/%m/%d"))

	# auth is a text file containining the account password
	# This is so you can automate this bot to run in the background via something like cron
	bot.login('pooroldmoot', open('auth').read())
	if not bot.loggedin:
		print('Failed to log in')
		exit(0)
	print('You are now logged in')
	print('You have %d adventures' % bot.adventures)

	bot.use_skill('advanced cocktailcrafting', 5)

	# Use the still 10 times for whatever booze items you have
	boozes = ['bottle of vodka', 'bottle of gin', 'bottle of whiskey', 'boxed wine']
	garnishes = ['olive','strawberry','lemon','grapefruit','orange'] 
	for i in xrange(5):
		item = random_item(bot, boozes)
		if item is not None:
			bot.use_still(item)
		else:
			break
		
	for _ in xrange(5):
		item = random_item(bot, garnishes)
		if item is not None:
			bot.use_still(item)
		else:
			break
		
	# Eat some burritos
	for _ in xrange(5):
		if bot.consume('food', 'insanely spicy bean burrito'):
			print('Ate an insanely spicy bean burrito')		

	# Make some cocktails
	drinks = db.get_all_drinks()
	drinksmap = {}
	for drink in drinks:
		drinksmap[drink] = drinks[drink].potency
		if bot.can_craft(drink):
			while bot.craft('cocktail', drink):
				print "Mixed a %s" % drink

	# All you can drink!
	if bot.drunk < 19:
		drink = random_item(bot, drinksmap.keys())
		while drink is not None and bot.drunk < 20 - drinksmap[drink] and bot.consume('booze', drink):
			drink = random_item(bot, drinks.keys())
			print('Drank a %s' % drink)

	# Time to go on an adventure!
	print('Starting with %d adventures' % bot.adventures)
	while bot.has_adventures():
		# use these every 10 adventures
		if bot.adventures % 10 == 0:
			bot.use_item('bag of Cheat-Os')
			bot.use_skill('disco fever')
			bot.use_skill('disco leer')
		if bot.hp < 40:
			bot.use_skill('disco nap', 2)
			print('Used disco power nap twice')
		bot.adventure(110)
		if(bot.adventures % 25 == 0):
			print("%d adventures left, current hp: %d" % (bot.adventures, bot.hp))
	# A nightcap
	[bot.consume('booze', item) for item in drinks if bot.inv_qty(item) > 0]
	bot.update()
	print("Logging out. New meat total: %d." % bot.meat)
	bot.logout()

def random_item(bot, items):
	random.shuffle(items)
	for item in items:
		if(bot.inv_qty(item) > 0):
			return item
	return None

if __name__ == '__main__':
	main()