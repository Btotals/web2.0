# -*- coding:utf-8 -*-
import re
import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class info:
	def __init__(self, name, section, card, cardType):
		self.name = name
		self.section = section
		self.card = card
		self.cardType = cardType
	def infoString(self):
		infoString = self.name + ";" + self.section  + ";" + self.card + ";" + self.cardType + "\n"
		return infoString

def writeToFile(path, content):
	fs = open(path, "a")
	fs.write(content)
	fs.close()

def readFromFile(path):
	fs = open(path)
	allLines = fs.read()
	return allLines

def Luhn(cardNumberString):
	sum = 0
	card = list(cardNumberString[::-1])
	cardLength = len(card)
	for index, number in enumerate(card):
		if (cardLength - index - 1) % 2 == 1:
			sum += int(number)
		else:
			doubleNum = int(number) * 2
			if doubleNum < 10:
				sum += doubleNum
			else:
				sum += doubleNum / 10 + doubleNum % 10
	flag = True if sum % 10 == 0 else False
	return flag

def checkCardNumber(cardType, cardNumberString):
	pattern1 = re.compile('\d+');
	pattern2 = re.compile('(\d{4}-){3}\d{4}')
	check = True
	if pattern1.match(cardNumberString) or pattern2.match(cardNumberString):
		card = cardNumberString.replace('-', '')
		if len(card) < 16:
			check = False
		else:
			if (cardType == "Visa" and card[0] != '4') or (cardType == "MasterCard" and card[0] != '5'):
				check = False
			else:
				check = Luhn(card)
	return check

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('buyagrade.html')

class infoHandler(tornado.web.RequestHandler):
	def post(self):
		name = self.get_argument("name", None)
		section = self.get_argument("section", None)
		card = self.get_argument("card", None)
		cardType = self.get_argument('card-type', None)
		filepath = os.path.join(os.path.dirname(__file__), "static/info/sucker.txt")
		infoMessage = ''
		cardErr = False
		if name == None or section == None or card == None or cardType == None:
			err = True
		else:
			if checkCardNumber(cardType, card) == True:		
				err = False
				infoMessage = info(name, section, card, cardType)
				writeToFile(filepath, infoMessage.infoString())
			else:
				err = True
				cardErr = True
		allLines = readFromFile(filepath)
		self.render('sucker.html', infoMessage=infoMessage,allLines=allLines, err=err, cardErr=cardErr)

if __name__ == '__main__':
	tornado.options.parse_command_line()
	app = tornado.web.Application(
		handlers=[(r'/', IndexHandler),(r'/sucker', infoHandler)],
		template_path=os.path.join(os.path.dirname(__file__), "template"),
		static_path=os.path.join(os.path.dirname(__file__), "static"),autoescape = None,debug = True
	)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
