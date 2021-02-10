import logging
from datetime import date

"""
Class that allows managing the logs generated by Telk-Alert-Tool.
"""
class Logger:

	"""
	Method that allows to write the application logs in a file.

	Parameters:
	self -- An instantiated object of the Logger class.
	message -- Message to be shown in the log.
	type_log -- Type of log to write.
	"""
	def createLogAgent(self, message, type_log):
		logger = logging.getLogger('Telk_Alert_Agent_Log')
		logger.setLevel(logging.INFO)
		fh = logging.FileHandler('/var/log/Telk-Alert/telk_alert_agent_log' + str(date.today()) + '.log')
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