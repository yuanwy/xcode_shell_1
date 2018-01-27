#coding=utf-8
#!/usr/local/bin/python3
#
import re
import os
import sys

import re
import time
import shutil
import MySQLdb


from ftplib import FTP

BUILD_MODE = os.getenv("MODE")
#BUILD_MODE = "None"
BUILD_CONFIG = os.getenv("TYPE")
#BUILD_CONFIG = 'Debug'

#配置项目构建路径
WORKSPACE = os.getenv("WORKSPACE")
#WORKSPACE = "/Users/admin/workspace/IOS/EJX-ios"
BUILDPACKPATH = "/Users/admin/Library/Developer/Xcode/DerivedData/Build/Products/"
KEYCHAINPATH = "/Users/admin/Library/Keychains/login.keychain-db"
KEYCHAINPASSWORD = "123456"

#配置数据库MySQL
MYSQL_HOST = "197.255.20.22"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWD = "yjp_uat"
MYSQL_DB = "package"

#配置FTP
FTP_HOST = "197.255.20.22"
FTP_PORT = 21
FTP_USER = "pack"
FTP_PASSWD = "861020"

#配置编译参数

NOTICE = "0"
PROVISIONING = "Manual"
CODE_SIGN_STYLE = "Manual"
PROVISIONING_PROFILE = "b935ea7f-1252-48d6-83e0-dec54a2bb013"
#PROVISIONING_PROFILE = "195b46fe-efc1-4e9b-9f2f-245a5ab470e0"
#PROVISIONING_PROFILE_SPECIFIER = "yijiupi_d"
PROVISIONING_PROFILE_SPECIFIER = "wildcardApp"
PRODUCT_BUNDLE_IDENTIFIER = ""
CODE_SIGN_IDENTITY = "iPhone Distribution"
DEVELOPMENT_TEAM = "NYHMQDP422"

TITLE = {
	"EJPProject":"易酒批",
    "EJPPurchase":"易酒采",
    "EJPDeliver":"易配送",
    "EJPBroker":"经纪人",
	"EJPDealerProject":"易经销",
	"EJPInBusinessDeliver":"入驻商易配送",
}

class Build(object):
	def __init__(self):
		global PRODUCT_BUNDLE_IDENTIFIER
		self.target_name = self.get_target_name()
		PRODUCT_BUNDLE_IDENTIFIER = "com.huiayi." + self.target_name

	def connectdb(self,pjectname,config,date,title):
		try:
			conn = MySQLdb.connect(host=MYSQL_HOST,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASSWD,db=MYSQL_DB,charset="utf8")
			cursor = conn.cursor()
			sql = "insert into iospack_projectinfo(pname,ptype,pdate,ptitle) values ('%s','%s','%s','%s') on duplicate key update pname='%s',ptype='%s',pdate='%s',ptitle='%s'" %(pjectname,config,date,title,pjectname,config,date,title)
			cursor.execute(sql)
			conn.commit()
			print("Update database success")
		except:
			#Rollback in case there is any error
			conn.rollback()
			print("Insert data error,Rollback database success")
			sys.exit(1)
		#关闭数据库连接
		conn.close()

	def ipa_path(self):
		path = WORKSPACE + '/' + 'ipa_build'
		if os.path.exists(path):
			os.system('rm -rf %s' %path)
			os.makedirs(path)
		else:
			os.makedirs(path)
		return path

	def app_path(self):
		if BUILD_CONFIG == "Debug":
			sou_path = BUILDPACKPATH + 'Debug-iphoneos' + '/' + self.target_name + '.app'
			return sou_path
		if BUILD_CONFIG == "Release":
			sou_path = BUILDPACKPATH + 'Release-iphoneos' + '/' + self.target_name + '.app'
			return sou_path
		if BUILD_CONFIG == "Distribute":
			sou_path = BUILDPACKPATH + 'Distribute-iphoneos' + '/' + self.target_name + '.app'
			return sou_path

	def get_target_name(self):
		target_name = os.popen("ls %s | grep xcodeproj | awk -F.xcodeproj '{print $1}'" %WORKSPACE)
		return target_name.read().replace('\n','')

	def allowkeychain(self):
	    # User interaction is not allowed
	    os.system("security unlock-keychain -p '%s' %s"%(KEYCHAINPASSWORD,KEYCHAINPATH))
	    return

	def pod_update(self):
		# Update code and pod version
		os.system("export LANG=en_US.UTF-8;LANGUAGE=en_US.UTF-8;LC_ALL=en_US.UTF-8 && cd %s;/usr/local/bin/pod update" %WORKSPACE)
		print("Update code and pod version is success")
		return

	def cleanPro(self):
		os.system('xcodebuild -configuration %s clean' %BUILD_CONFIG)
		os.system('rm -rf %s' %BUILDPACKPATH)
		print("Clean is success")
		return

	def modify(self,pfile,efile):
		self.mod_notif(efile)
		mod_dic = {"notice":[NOTICE,"(enabled) = (\d)\;"],
		    "provisioningstyle":[PROVISIONING,"(ProvisioningStyle) = (\w+)\;"],
		    "code_sign_style":[CODE_SIGN_STYLE,"(CODE_SIGN_STYLE) = (\w+)\;"],
		    "provisioning_profile":[PROVISIONING_PROFILE,"(PROVISIONING_PROFILE) \= ([\'|\"][a-z0-9-]+[\'|\"]|[\'|\"][\'|\"])\;"],
		    "provisioning_profile_specifier":[PROVISIONING_PROFILE_SPECIFIER,"(PROVISIONING_PROFILE_SPECIFIER) = (\w+|\"\")\;"],
			"product_bundle_identifier":[PRODUCT_BUNDLE_IDENTIFIER,"(PRODUCT_BUNDLE_IDENTIFIER) = ((\w+.)+);"],
			"code_sign_identity":[CODE_SIGN_IDENTITY,"\"(CODE_SIGN_IDENTITY.*\])\" = \"(.*)\"\;"],
			"development_team":[DEVELOPMENT_TEAM,"(DEVELOPMENT_TEAM) = \"(.*)\";"],
			}
		#try:
		#lines = open(pfile,'r').readlines()
		with open(pfile, mode='r+', encoding='utf-8') as f:
			lines = f.readlines()
			flen = len(lines) - 1
			for k,v in mod_dic.items():
				for i in range(flen):
					rule = re.compile(v[1])
					result = rule.search(lines[i])
					if result:
						print("this is new vlu %s" %v[0])
						print("Old vlu %s" %result.group(2))
						lines[i] = lines[i].replace(result.group(2),v[0])
			with open(pfile, mode='w+', encoding='utf-8') as fw:
				fw.writelines(lines)
			
			#except Exception, e:
			#	print e

	def mod_notif(self,efile):
		context = """
	<?xml version="1.0" encoding="UTF-8"?>
	<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
	<plist version="1.0">
		<dict/>
	</plist>
	"""
		f = open(efile,'w')
		f.write(context)
		f.close()



	def build_app(self):
		timeStamp=time.time()
		timeArray = time.localtime(timeStamp)
		otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
		#print(self.connectdb(self.target_name,BUILD_CONFIG,otherStyleTime))
		work_path = WORKSPACE + '/' + self.target_name + '.xcworkspace'
		plist_file = WORKSPACE + '/' + self.target_name + '.xcodeproj' + '/' + 'project.pbxproj'
		noti_file = WORKSPACE + '/' + self.target_name + '/' + self.target_name + '.entitlements'
		self.pod_update()
		self.modify(plist_file,noti_file)
		self.allowkeychain()
		self.cleanPro()
		build_result = os.system('xcodebuild -workspace %s -scheme %s -configuration %s ONLY_ACTIVE_ARCH=NO' %(work_path,self.target_name,BUILD_CONFIG))
		if build_result == 0:
			ipa_path = self.ipa_path() + '/' + self.target_name + '-' + BUILD_CONFIG + '.ipa'
			app_path = self.app_path()
			ipa_result = os.system('xcrun -sdk iphoneos PackageApplication -v %s -o %s' %(app_path,ipa_path))
			if ipa_result == 0:
				print('Build Success')
				split_name = os.path.basename(ipa_path).split('.')[0]
				project_name = TITLE[self.target_name] + split_name
				self.connectdb(project_name,split_name,otherStyleTime,split_name)
				self.ftp_up(ipa_path)

		else:
			print("** BUILD FAILED **")

	def ftp_up(self,filename):
		ftp = FTP()
		ftp.set_debuglevel(2)
		ftp.connect(FTP_HOST,FTP_PORT)
		ftp.login(FTP_USER,FTP_PASSWD)
		ftp.cwd('IOS/EJP')
		bufsize = 1024
		file_handler = open(filename,'rb')
		ftp.storbinary('STOR %s' % os.path.basename(filename),file_handler,bufsize)
		ftp.set_debuglevel(0)
		file_handler.close()
		ftp.quit()
		print("ftp up OK")

	def up_ipa(self):
		timeStamp=time.time()
		timeArray = time.localtime(timeStamp)
		otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
		workpath = "/Users/admin/workspace/IOS/Online/"
		plist = os.listdir(workpath)
		for i in plist:
			if "ipa" in i:
				self.connectdb(i,i,otherStyleTime,"pack")
				base_path = os.path.join(workpath,i)
				self.ftp_up(base_path)
       
		

app = Build()
if BUILD_MODE == None:
	print ("************************************%s" %BUILD_MODE)
	print ("************************************%s" %BUILD_CONFIG)
	#sys.exit(1)
	app.build_app()
else:
	print ("************************************%s" %BUILD_MODE)
	print ("************************************%s" %BUILD_CONFIG)
	#sys.exit(1)
	app.up_ipa()
#app.transf_data()
#plist_file = WORKSPACE + '/' + app.target_name + '.xcodeproj' + '/' + 'project.pbxproj'
#noti_file = WORKSPACE + '/' + app.target_name + '/' + app.target_name + '.entitlements'
#app.modify(plist_file,noti_file)
