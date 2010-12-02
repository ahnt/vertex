#!/usr/bin/env python

from quixote.publish import Publisher
from quixote.directory import Directory
from quixote.util import StaticDirectory
import quixote
from urllib import quote_plus
import pkg_resources
import os.path
import jinja2
from quixote.form import Form, StringWidget, PasswordWidget
from sqlite3 import *
import startami
from session2.Session import Session as _Session
from quixote import get_user, get_session, get_session_manager, get_field


class Session(_Session, object):
    def __init__(self, id):
        super(Session, self).__init__(id)
        self.message = None
        self.my_chemicals = []
        self.my_message = None
        self.my_removed = []
        self.search = None

    def __str__(self):
        return "<Session %s>" % pprint.pformat(vars(self))
	
	def set_user(self, user):
		self.user = user.db_id
	
	def get_user(self):
		if self.user is None:   # user not set
			return None
		return database.load_user(self.user)

    def has_info(self):
        return True

class myFirstUI(Directory):
	_q_exports = ['','A', 'B','css','imageFolder','dataSubmitted','login','registerThisUser']
	imageFolder=StaticDirectory('/Volumes/KoMoDo/science/WebRelated/myFirst/mySubfolder', list_directory=1)
	def __init__(self):
		self.theLoginText="""<form name="theLogin" action="login" method="post">login: <input type="text" name="user" />password: <input type="password" name="pwd" /><input type="submit" name="loginButton" value="login" /><input type="submit" name="registerButton" value="register" /></form>"""
		self.theLogoutText="""<form name="theLogin" action="login" method="post"><input type="submit" name="logoutButton" value="logout" /></form>"""
		self.registerText=self.theLoginText
		
	def _q_index(self):
		registerText=self.registerText
#		template = env.get_template('BasicView/index.html')
		myVariable=templatesdir
#		zipForm.add(Form.StringWidget, 'user_name', '[enter user name]',title='User name:',hint='Enter your name',size=40,required=False)
		template = env.get_template('myBase.html')
		theUser=get_user()
		print(theUser)
		return template.render(locals())

	def dataSubmitted(self):
		request = quixote.get_request()
		form = request.form
		k=request.form.keys();
		myData="<p>"+form['accessKey']+"</p><p>"+form['secretKey']+"</p><p>"+form['pkName']+"</p>"
		myVariable=templatesdir
		template = env.get_template('mySubmit.html')
		T=startami.prepareInstance('ubuntu1004x64', 'm1.large', form['accessKey'], form['secretKey'],form['pkName'], ['zsh', 'screen', 'git'],'thePIPELINEURL')
		val1=T(1)
		val2=T(2)
		return template.render(locals())
	
	def css(self):
		cssfile = os.path.join(templatesdir, 'myStyle.css')
		response = quixote.get_response()
		response.set_content_type('text/css')
		return open(cssfile).read()
			
	def login(self):
		request = quixote.get_request()
		form = request.form
		if form.has_key('registerButton'):
			myVariable=templatesdir
			template = env.get_template('myRegisterForm.html')
			return template.render(locals())
		elif form.has_key('logoutButton'):
			self.registerText=self.theLoginText
			registerText=self.registerText
			myVariable=templatesdir
			template = env.get_template('myBase.html')
			return template.render(locals())
		elif form.has_key('loginButton'):
			conn = connect('vertexUserDB.db')
			curs = conn.cursor()
			curs.execute("select * from item")
			identified=False
			for row in curs:
				print row
				if row[1]==form['user'] and row[2]==form['pwd']:
					accessKey=row[3]
					secretKey=row[4]
					pkName=row[5]
					identified=True
			if identified:
				self.registerText=self.theLogoutText
			else:
				self.registerText=self.theLoginText
			registerText=self.registerText
			myVariable=templatesdir
			template = env.get_template('myBase.html')
			return template.render(locals())
		
	def registerThisUser(self):
		request = quixote.get_request()
		form = request.form
		conn = connect('vertexUserDB.db')
		curs = conn.cursor()
		curs.execute("select user from item")
		identified=False
		for row in curs:
			if row[0]==form['user']:
				identified=True
		if identified:
			registrationFeedback="""<p>Sorry but this user already exists, please choose a different user name.</p>"""
		else:
			curs.execute("insert or replace into item values (NULL,'"+form['user']+"','"+form['pwd']+"','"+form['accessKey']+"','"+form['secretKey']+"','"+form['pkName']+"')")
			conn.commit()
			registrationFeedback="""<p>Congratulations, you are now a registered VERTEX user! When you now login, we will alredy know all the data required to process you pipeline.</p>"""
		myVariable=templatesdir
		template = env.get_template('myUserRegistered.html')
		return template.render(locals())
		
	def A(self):
		mfsfc=myFirstServices.firstClass;
		return '''<html><p>A</p></html>'''
		
	def B(self):
		mfsfc=myFirstServices.firstClass;
		return '''<html><p>B</p></html>'''
		
def session_manager():
	from session2.store.VolatileSessionStore import VolatileSessionStore
	store = VolatileSessionStore()
	#DirectorySessionStore(config.sessions_dir, create=True)
	from session2.SessionManager import SessionManager
	session_manager = SessionManager(store)
	return SessionManager(store, Session)

def create_publisher():
	#publisher=Publisher(myFirstUI(),display_exceptions='plain')
	#publisher=Publisher(myFirstUI(),session_manager)
	#quixote.DEFAULT_CHARSET = config.output_encoding
	publisher = Publisher(myFirstUI(),display_exceptions='plain',session_cookie_name="VORTEX_Session",session_manager=session_manager(),)
	return publisher

if __name__ == '__main__':
	thisdir = os.path.dirname(__file__)
	templatesdir = os.path.join(thisdir, 'mySubfolder')
	templatesdir = os.path.abspath(templatesdir)
	loader = jinja2.FileSystemLoader(templatesdir)
	env = jinja2.Environment(loader=loader)
		
	from quixote.server.simple_server import run
	print 'creating demo listening on http://localhost:8080/'
	run(create_publisher, host='user-e47d8b.user.msu.edu', port=8080)
	#run(create_publisher, host='localhost', port=8080)