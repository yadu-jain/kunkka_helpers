#Author: Heera
#Date: 2014-09-01
#Description: master server configuration wrapper
import ConfigParser
import os

CONFIG_FILE="server_config.ini"
ACTIVE_SECTION="active"

class Server_Config(object):
	def __init__(self, active_section=ACTIVE_SECTION):
		super(Server_Config, self).__init__()
		try:			
			global CONFIG_FILE
			
			self.config=ConfigParser.ConfigParser()
			path =  os.path.join(os.path.dirname(os.path.abspath(__file__)),CONFIG_FILE)
			self.config.read(path)	
			self.__table_schemas__ = {}		

			if not (active_section in self.config.sections()):
				raise Exception("active section "+active_section+" not defined !")
			else:
				config_section = self.config.get(active_section,"default_config_section")
				if not (config_section in self.config.sections()):
					raise Exception("active section "+config_section+" not found !")	
				#print "Default Server Config: %s" % config_section
				self.section = config_section
			self.loaded=True
		except Exception as ex:
			self.loaded=False
			self.loading_error=str(ex)

	def get_config(self,key):
		return self.config.get(self.section,key)

