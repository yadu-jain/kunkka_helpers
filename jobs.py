#Author: Heera
#Date: 2014-09-01
#Description: helpers for creating jobs
import multiprocessing as mp
import Queue
from multiprocessing.managers import SyncManager
from datetime import datetime,timedelta
import time
import pickle
AUTHKEY= "60c05c632a2822a0a877c7e991602543"
PORTNUM = 8004 #Preffered port
IP='127.0.0.1'#"10.66.60.90"
from collections import OrderedDict

def add_job(job,callback_list=[]):
	manager=JobsManager()
	if type(job)==tuple:
		if len(job)==2:
			job.add({})			
		if len(job)==0:
			raise Exception("Invalid job !")
	else:
		raise Exception("Invalid job !")

	job=(job[0],job[1],OrderedDict(sorted(job[2].items())))
	job_q=manager.get_job_q()
	db=manager.get_server_db()	
	row_id = db.add_job(job,callback_list)
	job_q.put(job + (row_id,))				
	del db,manager,job_q

class JobsWaiter(object):	
	# FAILED 	=-1
	# SUCCESS =0	
	ADDED 	=1
	WAITING =2

	@staticmethod
	def callback(response,**kwrd):	
		manager=JobsManager() #make_client_manager(IP,PORTNUM,AUTHKEY)
		# status_obj=manager.get_sync_data()
		req=response["request"]
		# process_id=req[2]["process_id"]
		waiter=JobsWaiter(manager,kwrd["name"])
		waiter.done_task(req)
		del manager
		del waiter

	def __init__(self,manager,name):		
		#self.waiter_queue=manager.get_waiter(name)		
		self.wait_list=manager.get_wait_list(name)		
		self.job_q=None
		self.callbacks_dict=None
		self.tasks=[]		
		self.manager=manager
		self.name=name
		self.to_push=[]		

	def get_callback_job(self):
		return ("helpers.jobs","JobsWaiter.callback",{"name":self.name})

	def z_add_job(self,obj):					
		self.manager.add_job(obj,	
							callback_list=[self.get_callback_job()])	
		#self.tasks.append(obj)
		self.wait_list[pickle.dumps(obj)]=JobsWaiter.ADDED

	def add_job(self,obj,push=False):
		## Add job to server callbacks
		if push==True:
			self.__push_task__(obj)
		else:
			self.to_push.append(obj)

	def done_task(self,obj):		
		del self.wait_list[pickle.dumps(obj)]

	def __push_task__(self,obj):
		## Add job to server callbacks
		job=obj
		callback_list=[self.get_callback_job()]

		if self.job_q is None:
			self.job_q=self.manager.get_job_q()

		if self.callbacks_dict is None:
			self.callbacks_dict=self.manager.get_callbacks_dict()		

		if type(job)==tuple:
			if len(job)==2:
				job.add({})			
			if len(job)==0:
				raise Exception("Invalid job !")
		else:
			raise Exception("Invalid job !")

		job=(job[0],job[1],OrderedDict(sorted(job[2].items())))
		
		req=job
		for callback_job in  callback_list:
			if type(job)==tuple:				
				if len(job)==2:
					job.add({})			
				if len(callback_job)==2:
					callback_job.add({})			
				if len(callback_job)==0:
					raise Exception("Invalid callbacks !")
				else:
					self.callbacks_dict[pickle.dumps(job)]=callback_job
					job=callback_job
			else:
				raise Exception("Invalid callbacks !")
		db=self.manager.get_server_db()		
		
		row_id = db.add_job(req)
		self.job_q.put(req+(row_id,))				
		## Add job to local wait list
		self.wait_list[pickle.dumps(req)]=JobsWaiter.ADDED

	def push_all(self):
		print "pushing tasks %d" %(len(self.to_push))
		for obj in self.to_push:
			self.__push_task__(obj)
		self.to_push=[]

	def wait(self,timeout=6*60*60,finish=True):
		dt_start=datetime.now()
		curr_timeout=timeout
		print "waiting in sink"
		try:			
			time.sleep(1)
			self.push_all()
			while len(self.wait_list.keys())>0 and curr_timeout>0:
				diff = datetime.now() - dt_start				
				curr_timeout = timeout - int(diff.total_seconds())
				time.sleep(1)
				print "waiting tasks=%d\ttimeout=%d" % (len(self.wait_list.keys()),curr_timeout)
			self.manager.delete_waiter(self.name)
		except Exception as e:
			print e

	def get_tasks(self):
		return self.tasks

##-----------------------------------New API-------------------------------------###

class JobsManager(SyncManager):
	"""
	"""
	def __init__(self):
		super(JobsManager, self).__init__(address=(IP, PORTNUM), authkey=AUTHKEY)
		self.connect()
		print 'Client connected to %s:%s' % (IP, PORTNUM)

JobsManager.register('add_job')	
JobsManager.register('get_server_db')	
JobsManager.register('get_job_q')	
JobsManager.register('get_sync_data')	
JobsManager.register('get_callbacks_dict')	
JobsManager.register('get_waiter')	
JobsManager.register('delete_waiter')
JobsManager.register('get_wait_list')	

##-----------------------------------------------------------------------------##

## Older API ####
class JobsConsumer(SyncManager):
	pass
JobsConsumer.register('add_job')	
JobsConsumer.register('get_sync_data')	
JobsConsumer.register('get_callbacks_dict')	
JobsConsumer.register('get_waiter')	
JobsConsumer.register('delete_waiter')
JobsConsumer.register('get_wait_list')	
		
def make_client_manager(ip, port, authkey):
	""" Create a manager for a client. This manager connects to a server on the
		given address and exposes add_job method to add job.
		Return a manager object.
	"""
	JobsConsumer.register('add_job')	
	JobsConsumer.register('get_sync_data')	
	JobsConsumer.register('get_callbacks_dict')	
	JobsConsumer.register('get_waiter')	
	JobsConsumer.register('get_wait_list')	
	JobsConsumer.register('delete_waiter')

	manager = JobsConsumer(address=(ip, port), authkey=authkey)
	manager.connect()

	print 'Client connected to %s:%s' % (ip, port)
	return manager