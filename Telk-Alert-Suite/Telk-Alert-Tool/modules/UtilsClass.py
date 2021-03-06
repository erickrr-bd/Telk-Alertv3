import os
import pwd
import sys
import yaml
import logging
from datetime import date
from Crypto import Random
from hashlib import sha256
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad

"""
Class that allows managing all the utilities that are used for the operation of the application.
"""
class Utils:
	"""
	Property that saves the passphrase that will be used for the decryption process.
	"""
	passphrase = None

	"""
	Constructor for the Utils class.

	Parameters:
	self -- An instantiated object of the Utils class.
	"""
	def __init__(self):
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
			self.createLogTool(str(exception), 4)
			sys.exit(1)

	"""
	Method that creates a new route from the root path of Telk-Alert.

	Parameters:
	self -- An instantiated object of the Utils class.
	path_dir -- Folder or directory that will be added to the source path of Telk-Alert.

	Return:
	path_final -- Final directory.
	"""
	def getPathTalert(self, path_dir):
		path_root = "/etc/Telk-Alert-Suite/Telk-Alert"
		path_final = os.path.join(path_root, path_dir)
		return path_final

	"""
	Method that creates a new route from the root path of Telk-Alert-Agent.

	Parameters:
	self -- An instantiated object of the Utils class.
	path_dir -- Folder or directory that will be added to the source path of Telk-Alert-Agent.
	"""
	def getPathTagent(self, path_dir):
		path_origen = "/etc/Telk-Alert-Suite/Telk-Alert-Agent"
		path_agent = os.path.join(path_origen, path_dir)
		return path_agent

	"""
	Method that obtains the passphrase used for the process of encrypting and decrypting a file.

	Parameters:
	self -- An instantiated object of the Utils class.

	Return:
	pass_key -- Passphrase in a character string.

	Exceptions:
	FileNotFoundError -- his is an exception in python and it comes when a file does not exist and we want to use it. 
	"""
	def getPassphrase(self):
		try:
			file_key = open(self.getPathTalert('conf') + '/key','r')
			pass_key = file_key.read()
			file_key.close()
			return pass_key
		except FileNotFoundError as exception:
			self.createLogTool(str(exception), 4)
			sys.exit(1)

	"""
	Method that validates data from a regular expression.

	self -- An instantiated object of the Utils class.
	regular_expression -- Regular expression with which the data will be validated.
	data -- Data to be validated.
	"""
	def validateRegularExpression(self, regular_expression, data):
		if(not regular_expression.match(data)):
			return False
		return True

	"""
	Method that changes the uid and gid of a file for that of telk_alert.

	Parameters:
	self -- An instantiated object of the Utils class.
	path -- Path where the file or directory is located.
	"""
	def changeUidGid(self, path):
		try:
			uid = pwd.getpwnam('telk_alert').pw_uid
			gid = pwd.getpwnam('telk_alert').pw_gid
			os.chown(path, uid, gid)
		except OSError as exception:
			self.createLogTool(str(exception), 4)
			sys.exit(1)

	"""
	Method that obtains the hash of a particular file.

	Parameters:
	self -- An instantiated object of the Utils class.
	file -- Path of the file from which the hash function will be obtained.
	form_dialog -- A FormDialogs class object.

	Return:
	Hash obtained.

	Exceptions:
	Exception -- Thrown when any mistake happens.
	"""
	def getSha256File(self, file, form_dialog):
		try:
			hashsha = sha256()
			with open(file, "rb") as file_hash:
				for block in iter(lambda: file_hash.read(4096), b""):
					hashsha.update(block)
			return hashsha.hexdigest()
		except Exception as exception:
			form_dialog.d.msgbox("\nError getting the file's hash function. For more details, see the logs.", 7, 50, title = "Error message")
			self.createLogTool(str(exception), 4)
			form_dialog.mainMenu()

	"""
	Method that encrypts a text string.

	Parameters:
	self -- An instantiated object of the Utils class.
	text -- Text to encrypt.
	form_dialog -- A FormDialogs class object.

	Return:
	Encrypted text.
	"""
	def encryptAES(self, text, form_dialog):
		try:
			text_bytes = bytes(text, 'utf-8')
			key = sha256(self.passphrase.encode()).digest()
			IV = Random.new().read(AES.block_size)
			aes = AES.new(key, AES.MODE_CBC, IV)
			return b64encode(IV + aes.encrypt(pad(text_bytes, AES.block_size)))
		except Exception as exception:
			form_dialog.d.msgbox("\nFailed to encrypt the data. For more details, see the logs.", 7, 50, title = "Error message")
			self.createLogTool(str(exception), 4)
			form_dialog.mainMenu()

	"""
	Method that decrypts a text string.

	Parameters:
	self -- An instantiated object of the Utils class.
	text_encrypt -- Text to decipher.
	form_dialog -- A FormDialogs class object.

	Return:
	Character string with decrypted text.

	Exceptions:
	binascii.Error -- Is raised if were incorrectly padded or if there are non-alphabet characters present in the string. 
	"""
	def decryptAES(self, text_encrypt, form_dialog):
		try:
			key = sha256(self.passphrase.encode()).digest()
			text_encrypt = b64decode(text_encrypt)
			IV = text_encrypt[:AES.block_size]
			aes = AES.new(key, AES.MODE_CBC, IV)
			return unpad(aes.decrypt(text_encrypt[AES.block_size:]), AES.block_size)
		except binascii.Error as exception:
			form_dialog.d.msgbox("\nFailed to decrypt the data. For more details, see the logs.", 7, 50, title = "Error message")
			self.createLogTool(str(exception), 4)
			form_dialog.mainMenu()

	"""
	Method that writes the logs generated by the application in a file.

	Parameters:
	self -- An instantiated object of the Logger class.
	message -- Message to be shown in the log.
	type_log -- Type of log to write.
	"""
	def createLogTool(self, message, type_log):
		name_log = '/var/log/Telk-Alert/telk-alert-tool-log-' + str(date.today()) + '.log'
		logger = logging.getLogger('Telk_Alert_Tool_Log')
		logger.setLevel(logging.INFO)
		fh = logging.FileHandler(name_log)
		logger.addHandler(fh)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fh.setFormatter(formatter)
		logger.addHandler(fh)
		if type_log == 1:
			logger.debug(message)
		if type_log == 2:
			logger.info(message)
		if type_log == 3:
			logger.warning(message)
		if type_log == 4:
			logger.error(message)
		if type_log == 5:
			logger.critical(message)
		self.changeUidGid(name_log)