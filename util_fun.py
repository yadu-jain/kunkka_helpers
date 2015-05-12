#from helpers 
import db
import server_config as config
#GDS_USERNAME="agn"
#GDS_PASSWORD="t0w3r47556br!dg3"
#refresh_routes_url="http://gds.beta.travelyaari.com/service_report_ajax/refresh_new_trip?shared_key=b218fad544980213a25ef18031c9127e&PROVIDER_TRIP_ID=$provider_trip_id&PROVIDER_ID=$provider_id&STR_FROM_JOURNEY_DATE=$from_jd&STR_TO_JOURNEY_DATE=$to_jd"

server_config=config.Server_Config()
REFRESH_ROUTES_URL=server_config.get_config("refresh_routes_url")
GDS_USERNAME=server_config.get_config("gds_username")
GDS_PASSWORD=server_config.get_config("gds_password")

def get_process_id(provider_id):
	"""
		return process_id from gdsdb for given provider
	"""
	str_sql="""
	DECLARE @process_id INT=0
	EXEC get_process_id %d,@process_id OUT
	SELECT 	@process_id
	"""	
	gds_db = db.DB("gdsdb","gds",GDS_USERNAME,GDS_PASSWORD)	
	db_response = gds_db.execute_query(str_sql,params=(provider_id,),commit=True)#("get_process_id",(provider_id,process_id))
		
	if len(db_response)>0 and db_response[0]["PROCESS_ID"]>0:
		return db_response[0]["PROCESS_ID"]
	else:
		raise Exception("Process Id found as 0!")

def refresh_routes(provider_trip_id,provider_id,from_jd,to_jd):		
	"""	
		from_jd: string date(YYYY-MM-DD)
		to_jd: string date(YYYY-MM-DD)
	"""
	url=refresh_routes_url
	url=url.replace("$provider_trip_id",str(provider_trip_id))
	url=url.replace("$provider_id",str(provider_id))
	url=url.replace("$from_jd",from_jd)
	url=url.replace("$to_jd",to_jd)
	import urllib2
	return urllib2.urlopen(url).read()
###-----------------------------------------------------------------------####
if __name__=='__main__':
	print get_process_id(1)