#Author: Heera
#Date: 2014-08-26
#Description: Provider function modules

CONFIG_FILE="gds_api.ini"
DEFAULT_SECTION="dev"



from helpers import provider_exceptions,db,socks
import httplib2,json,urllib,xmltodict,re,time,os  
from datetime import datetime
from suds.client import Client
import json
import suds


__client__=None
class GDS_API:
	def __init__(self,section):
		try:
			import ConfigParser
			global CONFIG_FILE			
			self.section=section
			self.config=ConfigParser.ConfigParser()
			path =  os.path.join(os.path.dirname(os.path.abspath(__file__)),CONFIG_FILE)
			self.config.read(path)			
			print self.config.sections()
			if not (section in self.config.sections()):
				raise Exception("Section "+section+" not Found !")
			self.loaded=True			
		except Exception as ex:
			self.loaded=False
			self.loading_error=str(ex)

	def __get_client__(self,refresh=False):	
		"""
			soap client is cached in module using sud's object caching
		"""	
		import logging
		global __client__
		main_url = self.get_config("api_url")				
		if __client__ == None or refresh==True:
			__client__=Client(main_url,faults=True, retxml=True)
			logging.getLogger('suds.client').setLevel(logging.CRITICAL)			
			cache = __client__.options.cache
			cache.setduration(days=1)					
		return __client__.service	

	def get_default_auth(self):
		dict_auth={"UserID":self.get_config("auth.UserID"),"UserType":self.get_config("auth.UserType"),"Key":self.get_config("auth.Key")}
		return dict_auth

	def get_config(self,key):
	    return self.config.get(self.section,key)    
	    	
	def call(self,api_name,*args,**kwrds):
		try:
			service=self.__get_client__()
			#if service!=None and hasattr(service,api_name):
			api_method=getattr(service,api_name)
			response = api_method(*args,**kwrds)
			return response
		except suds.WebFault as detail:
			raise Exception("GDS API Error ! | "+str(detail))

def call(api_name,*args,**kwrds):
	"""
		Use this method to call directly gds api without worrying about Authentication and caching of wsdl
	"""
	import xmltodict

	api = GDS_API(DEFAULT_SECTION)	
	if not "Authentication" in kwrds:
		kwrds["Authentication"] = api.get_default_auth()
	response = api.call(api_name,*args,**kwrds)
	dict_response=xmltodict.parse(response)	
	if "soap:Envelope" in dict_response and "soap:Body" in dict_response["soap:Envelope"]:
		return dict_response["soap:Envelope"]["soap:Body"]
	else:
		raise Exception("Invalid GDS Response")


if __name__=="__main__":
	import xmltodict
	api = GDS_API(DEFAULT_SECTION)		
	dict_search_request={"FromCityId":2445,"ToCityId":2667,"JourneyDate":"2015-04-08"}
	dict_params={"SearchRequest":dict_search_request,"SecurityCode":"signature@776"}
	print datetime.now()
	#response = api.call("GetCPRoutesV6",**dict_params)
	#print datetime.now()
	#response = api.call("GetCPRoutesV6",**dict_params)	
	call("GetCPRoutesV6",**dict_params)
	print datetime.now()
	call("GetCPRoutesV6",**{"SearchRequest":dict_search_request,"SecurityCode":"signature@776"})
	print datetime.now()
	call("GetCPRoutesV6",**{"SearchRequest":dict_search_request,"SecurityCode":"signature@776"})
	print datetime.now()
	response = call("GetCPRoutesV6",**{"SearchRequest":dict_search_request,"SecurityCode":"signature@776"})
	print datetime.now()
	#print type(response)
	#print len(response.Route[0])	
	#dict_response=xmltodict.parse(response)	
	with open("output.txt","wb") as f:
	 	f.write(json.dumps(response,indent=4))
	 	f.flush()