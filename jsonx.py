from datetime import datetime 
import json
import decimal
def __date_handler__(obj):	
	if hasattr(obj, 'isoformat') :
		return obj.isoformat()
	elif isinstance(obj,decimal.Decimal):
		return float(obj) 
	else:
		return json.JSONEncoder().default(obj)
		

def dumps(data,*args,**kwrd):
	return json.dumps(data,default=__date_handler__,*args,**kwrd)