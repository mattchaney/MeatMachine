#!/usr/bin/python
from MeatMachine import MeatMachine

# 51 = Menagerie lvl1, 53 = Menagerie lvl2, 110 = icy peak 
bot = MeatMachine()
bot.login()
bot.use_skill(5014, 3) # Advanced Cocktailcrafting
for x in range(15):
	bot.adventure(51)
for x in range(15):
	bot.adventure(53)
while bot.has_adventures():
	if bot.hp < 40:
		bot.use_skill(5011, 2)
		print 'used Disco Power Nap'
	bot.adventure(110)
print "You now have %d meat! Huzzah" % bot.meat
bot.logout()