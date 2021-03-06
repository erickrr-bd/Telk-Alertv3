import os
import sys
import yaml
import time
import binascii
from hashlib import sha256
from base64 import b64decode
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from modules.LoggerClass import Logger

"""
Class that allows you to manage the utilities that the application will use for its operation.
"""
class Utils:
	"""
	Property that saves the passphrase that will be used for the decryption process.
	"""
	passphrase = None

	"""
	Property that stores an object of type Logger.
	"""
	logger = None

	"""
	Constructor for the Utils class.

	Parameters:
	self -- An instantiated object of the Utils class.
	"""
	def __init__(self):
		self.logger = Logger()
		self.passphrase = self.getPassphrase()

	"""
	Method that obtains the content of a file with the extension yaml.

	Parameters:
	self -- An instantiated object of the Utils class.
	file_yaml -- Yaml file path.

	Return:
	data_yaml -- Contents of the .yaml file stored in a list.

	Exceptions:
	IOError -- It is an error raised when an input/output operation fails.
	"""
	def readFileYaml(self, file_yaml):
		try:
			with open(file_yaml, 'r') as file:
				data_yaml = yaml.safe_load(file)
			return data_yaml
		except IOError as exception:
			self.logger.createLogTelkAlert(str(exception), 4)
			print("\nError reading YAML file. For more information see the application logs.")
			sys.exit(1)

	"""
	Method that reads the HTML template to send the alert via email.

	Parameters:
	self -- An instantiated object of the Utils class.
	json_message -- String that contains all the data obtained during the search.
	name_rule -- Name of the alert rule.

	Return:
	message -- Final message in HTML format.

	Exceptions:
	IOError -- It is an error raised when an input/output operation fails.
	"""
	def readTemplateEmail(self, json_message, name_rule):
		try:
			template_email = open(self.getPathTalert('modules/template/temp_email.html'), 'r')
			message = template_email.read()
			message = message.replace('nameRule', name_rule)
			message = message.replace('date', time.strftime("%c"))
			message = message.replace('esjson', json_message)
			template_email.close()
			return message
		except IOError as exception:
			self.logger.createLogTelkAlert(str(exception), 4)
			print("\nError reading the HTML template. For more information see the application logs.")
			

	"""
	Method that creates a new route from the root path of Telk-Alert.

	Parameters:
	self -- An instantiated object of the Utils class.
	path_dir -- Folder or directory that will be added to the source path of Telk-Alert.

	Return:
	path_final -- Final directory.
	"""
	def getPathTalert(self, path_dir):
		path_root = '/etc/Telk-Alert-Suite/Telk-Alert'
		path_final = os.path.join(path_root, path_dir)
		return path_final

	"""
	Method that obtains the passphrase used for the process of encrypting and decrypting a file.

	Parameters:
	self -- An instantiated object of the Utils class.

	Return:
	pass_key -- Passphrase in a character string.

	Exceptions:
	FileNotFoundError -- This is an exception in python and it comes when a file does not exist and we want to use it. 
	"""
	def getPassphrase(self):
		try:
			file_key = open(self.getPathTalert('conf') + '/key','r')
			pass_key = file_key.read()
			file_key.close()
			return pass_key
		except FileNotFoundError as exception:
			self.logger.createLogTelkAlert(str(exception), 4)
			print("\nKey File not found. For more information see the application logs.")	
			sys.exit(1)

	"""
	Method that converts a date to milliseconds.

	Parameters:
	self -- An instantiated object of the Utils class.
	datetime -- Date to convert.

	Return:
	milliseconds -- Milliseconds obtained from the conversion.

	Exceptions:
	TypeError -- The TypeError is thrown when an operation or function is applied to an object of an inappropriate type.
	"""
	def convertDateToMilliseconds(self, datetime):
		try:
			milliseconds = int(datetime.strftime("%s")) * 1000
			return milliseconds
		except TypeError as exception:
			self.logger.createLogTelkAlert(str(exception), 4)
			print("\nType Error:" + str(exception) + ". For more information see the application logs.")
			sys.exit(1)

	"""
	Method that converts a quantity expressed in a unit of time in milliseconds.

	Parameters:
	self -- An instantiated object of the Utils class.
	unit_time -- Unit of time in which the quantity is expressed.
	total_time -- Amount of time to convert.

	Return:
	Milliseconds obtained from the conversion.

	Exceptions:
	TypeError -- The TypeError is thrown when an operation or function is applied to an object of an inappropriate type.
	"""
	def convertTimeToMilliseconds(self, unit_time, total_time):
		try:
			if unit_time == 'minutes':
				return total_time * 60000
			if unit_time == 'hours':
				return total_time * 3600000
			if unit_time == 'days':
				return total_time * 86400000
		except TypeError as exception:
			self.logger.createLogTelkAlert(str(exception), 4)
			print("\nType Error:" + str(exception) + ". For more information see the application logs.")
			sys.exit(1)

	"""
	Method that converts a number of milliseconds into a date.

	Parameters:
	self -- An instantiated object of the Utils class.
	milliseconds -- Milliseconds to convert.

	Return:
	date -- Date obtained from the conversion.

	Exceptions:
	TypeError -- The TypeError is thrown when an operation or function is applied to an object of an inappropriate type.
	"""
	def convertMillisecondsToDate(self, milliseconds):
		try:
			date = datetime.fromtimestamp(milliseconds / 1000.0)
			date = date.strftime('%Y-%m-%d %H:%M:%S')
			return date
		except TypeError as exception:
			self.logger.createLogTelkAlert(str(exception), 4)
			print("\nType Error:" + str(exception) + ". For more information see the application logs.")
			sys.exit(1)

	"""
	Method that decrypts a text string.

	Parameters:
	self -- An instantiated object of the Utils class.
	text_encrypt -- Text to decipher.

	Return:
	Character string with decrypted text.

	Exceptions:
	binascii.Error -- Is raised if were incorrectly padded or if there are non-alphabet characters present in the string. 
	"""
	def decryptAES(self, text_encrypt):
		try:
			key = sha256(self.passphrase.encode()).digest()
			text_encrypt = b64decode(text_encrypt)
			IV = text_encrypt[:AES.block_size]
			aes = AES.new(key, AES.MODE_CBC, IV)
			return unpad(aes.decrypt(text_encrypt[AES.block_size:]), AES.block_size)
		except binascii.Error as exception:
			self.logger.createLogTelkAlert(str(exception), 4)
			print("\nDecryption failed. For more information see the application logs.")	
			sys.exit(1)