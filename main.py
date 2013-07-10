#!/usr/bin/python
'''
This is a sample main that is used for a Disco Bandit:
After logging in, the bot will cast Advanced Cocktailcrafting 
three times (the max per day) and then adventure in three
different areas. If your character's hp drops below 40
the bot will use the skill Disco Power Nap (which
heals for 40 hp) three times.
'''
from MeatMachine import MeatMachine

bot = MeatMachine()
bot.login()
bot.use_skill(5014, 5) # Advanced Cocktailcrafting
for _ in xrange(5):
	bot.consume('food', bot.get_id('insanely spicy bean burrito'))

while bot.has_adventures():
	if bot.hp < 40:
		bot.use_skill(5011, 2)
		print 'used Disco Power Nap'
	bot.adventure(110)
print "You now have %d meat! Huzzah" % bot.meat
bot.logout()
