#!/usr/bin/python
'''
This is a sample main that is used for a Disco Bandit.
time module is used to print date so output can be appended
to a log file
'''
import time
from MeatMachine import MeatMachine

def main():
	bot = MeatMachine()
	print(time.strftime("%Y/%m/%d"))

	# auth is a text file containining the account password
	# This is so you can automate this bot to run in the background via something like cron, ie
	auth = open('auth').read()
	bot.login('pooroldmoot', auth)
	if not bot.loggedin:
		return
	
	# Use the still 10 times for whatever booze items you have
	booze_list = ['vodka', 'gin', 'whiskey', 'rum', 'tequila', 'strawberry', 'olive']
	for _ in xrange(10):
		bot.still(get_booze(bot, booze_list))

	# Use Advanced Cocktailcrafting 5 times
	bot.use_skill(5014, 5)

	# Eat some burritos
	bot.consume('food', 'insanely spicy bean burrito', 5)

	# All you can drink!
	drinks = {'neuromancer':4, 'mae west':4, 'rabbit punch':4, 'parisian cathouse':4, 'vodka gibson':3}
	for name in drinks:
		while bot.drunk < 20 - drinks[name] and bot.consume('booze', name):
			print('Drank a %s' % name)

	# Time to go on an adventure!
	print('Starting with %d adventures' % bot.adventures)
	while bot.has_adventures():
		if bot.hp < 40:
			bot.use_skill(5011, 2)
			print('took 2 naps')
		bot.adventure(110)
		if(bot.adventures % 50 == 0):
			print("%d adventures left, current hp: %d" % (bot.adventures, bot.hp))

	print("New meat total: %d! Huzzah!!" % bot.meat)
	bot.logout()

def get_booze(bot, booze_list):
	for booze in booze_list:
		if(bot.inv_qty('bottle of ' + booze) > 0):
			return 'bottle of ' + booze

main()