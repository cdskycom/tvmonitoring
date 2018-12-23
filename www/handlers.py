# -*- coding: utf-8 -*-
from orm import User, Inspection, orm_to_dict, Schedule, InspectionType, Tag
from coroweb import get, post
from apis import APIValueError, APIError
from sqlalchemy.orm.exc import NoResultFound
from aiohttp import web, streamer
from config import configs
from const import const
import sys, logging, hashlib, base64, re, json, time, datetime, math, os
import trouble
import pdb
from uuid import uuid1

COOKIE_NAME = 'tvmonitorsession'
_COOKIE_KEY = configs.session.secret
_WEEK = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
#每日值班的班次，最多6班
_SCHEDULENUM = ['first', 'second', 'third','forth','fifth','sixth']  

def user2cookie(user, max_age):
	'''
	Generate cookie str by user.
	'''
	# build cookie string by: id-expires-sha1
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user['account'], user['password'], expires, _COOKIE_KEY)
	L = [user['account'], expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)

def cookie2user(cookie_str):
	'''
	Parse cookie and load user if cookie is valid.
	'''
	if not cookie_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) != 3:
			return None
		account, expires, sha1 = L
		if int(expires) < time.time():
			return None
		filters = {User.account == account}
		users = User.getAll(*filters)
		user = users[0]
		if user is None:
			return None
		s = '%s-%s-%s-%s' % (user['account'], user['password'], expires, _COOKIE_KEY)
		if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
			logging.info('invalid sha1')
			return None
		user['password'] = '******'

		return user
	except Exception as e:
		logging.exception(e)
		return None

@get('/signin')
async def signin():
	return {
		'__template__': 'signin.html'
	}
@get('/signout')
async def signout(request):
	referer = request.headers.get('Referer')
	r = web.HTTPFound(referer or '/')
	r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
	logging.info('user signed out.')
	return r

@get('/')
async def index(request):
	# logging.info('enter index...')
	# return {
	# 	'__template__': 'index.html'
	# }
	return {
		'__template__': 'dashboard.html'
	}

@get('/inspec')
async def getInspec(request):
	# logging.info('enter index...')
	# return {
	# 	'__template__': 'index.html'
	# }
	return {
		'__template__': 'index.html'
	}

@get('/manage')
async def manageIndex(request):
	logging.info('enter index...')
	return {
		'__template__': 'managebase.html'
	}


@get('/monitor_log')
async def monitorlog(request):
	return {
		'__template__': 'monitor_log.html'
	}

@get('/api/users')
async def api_users(*,page,items_perpage):
	page = int(page)
	items_perpage = int(items_perpage)
	userCount = User.getUserCount()
	totalPages = math.ceil(userCount / items_perpage)
	users = User.getUserPage(page,items_perpage)
	
	return dict(totalitems=userCount ,totalpage=totalPages, users=users)


@get('/api/users/{id}')
async def api_get_users(request, *, id):
	filters = {User.id == id}
	users = User.getAll(*filters)
	for user in users:
		user['password'] = "******"
	
	return dict(user=users[0])

_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


# 添加用户
@post('/api/users')
async def api_register_user(*, account, password, name, is_admin, support_provider_id, phone, email):
	logging.info('添加用户的密码: %s' % password)
	if not account or not account.strip():
		raise APIValueError('account','账号不能为空')
	if re.search(r'[\-\%\']+',account):
		raise APIValueError('account','账号不能包含特殊字符')
	if not password or not _RE_SHA1.match(password):
		raise APIValueError('password','密码不能为空')
	if not name or not name.strip():
		raise APIValueError('name','用户名不能为空')
	if not support_provider_id or int(support_provider_id) < 1:
		raise APIValueError('support_provider','支撑单位不能为空')
	if not phone or not phone.strip():
		raise APIValueError('phone','联系电话不能为空')

	filters = {User.account == account}
	users = User.getAll(*filters)
	if len(users) > 0:
		raise APIError('添加用户失败', 'account', '用户账号已经存在')
	sha1_passwd = '%s:%s' % (account, password)
	user = User(account, hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), name, is_admin, 
		support_provider_id, phone, email)
	user.save()
	res = dict()
	res['returncode'] = const.RETURN_OK
	res['message'] = '用户添加成功'
	# make session cookie:
	# r = web.Response()
	# 登录需要的设置cookie
	# r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	
	# r.body = json.dumps(orm_to_dict(user), ensure_ascii=False).encode('utf-8')
	return res

@post('/signin/authenticate')
async def authenticate(*, account, password):
	logging.info('登录用户的密码： %s' % password)
	if not account:
		raise APIValueError('account', '账号不能为空.')
	if re.search(r'[\-\%\']+', account):
		raise APIValueError('account','账号不能包含特殊字符')
	if not password:
		raise APIValueError('password', '密码无效.')
	filters = {User.account == account}

	users = User.getAll(*filters)
	if len(users) == 0:
		raise APIValueError('account', '用户不存在.')
	user = users[0]
	# check passwd:
	sha1 = hashlib.sha1()
	sha1.update(account.encode('utf-8'))
	sha1.update(b':')
	sha1.update(password.encode('utf-8'))
	logging.info('密码in db: %s , 计算的 %s' %(user['password'], sha1.hexdigest()) )
	if user['password'] != sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid password.')
	# authenticate ok, set cookie:
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user['password'] = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r

@post('/api/user/modifypassword/{id}')
async def api_modify_password(id, request, *, oldpassword, newpassword):
	if not oldpassword:
		raise APIValueError('password', '老密码不能为空')
	if not newpassword:
		raise APIValueError('password', '新密码不能为空')
	filters = {User.id == id}
	users = User.getAll(*filters)
	if len(users) == 0:
		raise APIValueError('account', '用户不存在.')
	user = users[0]
	account = user['account']
	# check passwd:
	sha1 = hashlib.sha1()
	sha1.update(account.encode('utf-8'))
	sha1.update(b':')
	sha1.update(oldpassword.encode('utf-8'))
	logging.info('密码in db: %s , 计算的 %s' %(user['password'], sha1.hexdigest()) )
	if user['password'] != sha1.hexdigest():
		raise APIValueError('passwd', '旧密码输入不正确')
		
	#重置新密码
	sha1_passwd = '%s:%s' % (account, newpassword)
	user = User.resetUser(id, hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest())
	user['password'] = "******"
	return  user


@post('/manage/api/user/update/{id}')
async def api_update_user(id, request, *, account, password, name, is_admin, phone, email):
	if not account or not account.strip():
		raise APIValueError('account','账号不能为空')
	if not name or not name.strip():
		raise APIValueError('name','用户名不能为空')
	if not phone or not phone.strip():
		raise APIValueError('phone','联系电话不能为空')
	user = User.getUserById(id)
	if user["account"] != account:
		raise APIValueError('account','登录账号不能修改')
	
	user = User.updateUser(id, name, is_admin, phone, email)
	user['password'] = "******"
	return  user

@post('/manage/api/user/reset/{id}')
async def api_reset_user(id, request, *, newpassword):
	if not newpassword  or not newpassword.strip():
		raise APIValueError('account','密码不能为空')
	user = User.getUserById(id)
	if not user:
		raise APIValueError('account','获取用户信息失败')
	
	account = user['account']
	sha1_passwd = '%s:%s' % (account, newpassword)
	
	user = User.resetUser(id, hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest())
	user['password'] = "******"
	return  user


@post('/manage/api/user/delete/{id}')
async def api_delete_user(id, request):
	res = dict()
	try:
		if User.deleteUser(id):
			res['returncode'] = 0
			res['message'] = '用户删除成功'
	except NoResultFound as e:
		res['returncode'] = 1
		res['error'] = 'deleteuser'
		res['message'] = "找不到相关记录"
	else:
		res['returncode'] = -1
		res['error'] = 'deleteuser'
		res['message'] = "用户删除失败，未知原因"

	
	return res

@get('/manage/user')
async def adduser():
	return {
		'__template__': 'user.html'

	}

@get('/manage/user/edit')
async def editUser(*, id):
	return {
		'__template__': 'user_edit.html',
		'id': id,
		'action': '/manage/api/user/update/%s' % id

	}

@get('/manage/user/add')
async def addUser():
	return {
		'__template__': 'user_edit.html',
		'id': '',
		'action': '/api/users'

	}


@get('/api/inspections')
async def api_get_inspections(request):

	inspections = Inspection.getAll()
	

	return dict(inspections=inspections)



@get('/manage/schedules')
async def schedule(request):
	return {
		'__template__': 'schedules.html'
	}

# 添加值班计划接口
# startTime:值班计划开始日期
# endTime：值班计划结束日期（不包含）
# users:计划值班人员名单
# shiftnms:每天的班次，比如每天1班，2班，3班等
# exchangeTime: 换班时间，当前只是用白班换班时间，其余班次按总班次计算得出
# needInspectionTask:创建值班计划时是否生成对应巡检任务
@post('/api/addschedules')
async def api_add_schedules(*, startDate, endDate, users, shiftnums, exchangeTime, insInterval, needInspectionTask=False):
	try:
		st = time.strptime(startDate, '%Y-%m-%d')
		et = time.strptime(endDate, '%Y-%m-%d')
		#白班交接时间,其他班次按此时间计算
		exchangeTimeDay = time.strptime(exchangeTime['day'], '%H:%M')	
		schedulStartTime = datetime.datetime(st.tm_year, st.tm_mon, st.tm_mday)
		schedulEndTime = datetime.datetime(et.tm_year, et.tm_mon, et.tm_mday)

		# 需要排值班计划的天数
		scheduleDays = (schedulEndTime - schedulStartTime).days		
	except Exception as e:
		raise APIValueError('schedule','日期格式不正确')
	if et <= st:
		raise APIValueError('schedule','结束日期不能小于等于开始日期')
	if len(users) < shiftnums:
		raise APIValueError('schedule','计划值班用户不能为空')

	filters = {Schedule.startTime >= startDate, Schedule.endTime <= endDate}
	schedules = Schedule.getAll(*filters)
	if len(schedules) > 0:
		raise APIError('添加值班计划失败', 'schedule', '指定日期范围内的值班计划已经存在')


	currentDate = schedulStartTime
	while currentDate < schedulEndTime:
		#创建值班计划
		startTime = currentDate + datetime.timedelta(hours=(exchangeTimeDay.tm_hour))

		for i in range(shiftnums):
			title = currentDate.strftime('%Y-%m-%d') + '-' + _WEEK[currentDate.weekday()] + '-' + _SCHEDULENUM[i]
			endTime = startTime + datetime.timedelta(hours = 24/shiftnums)
			onDutyUsers = getUserName('|', users[_SCHEDULENUM[i]])
			newschedule = Schedule(title, startTime, endTime, onDutyUsers)
			s = newschedule.save()
			logging.info('新增计划：%s' % s)
			if needInspectionTask:
				sid = s['id']
				stitle = s['title']
				#新增Inspection
				inspectTime = startTime
				while inspectTime < endTime:
					#新增Inspection
					inspectType = 'CGXJ'
					inspectTypeName = '常规巡检'
					if inspectTime == startTime:
						inspectType = 'JBXJ'
						inspectTypeName = '交班巡检'
					newInspecion = Inspection(inspectTime, sid, stitle, datetime.datetime.now(), datetime.datetime.now(), inspectType, inspectTypeName)
					newInspecion.save()
					inspectTime += datetime.timedelta(hours = int(insInterval))
	
			startTime = endTime

		currentDate += datetime.timedelta(days=1)

	res = dict()
	res['returncode'] = 0
	res['message'] = '值班计划添加成功'
	return res

# 帮助函数，根据用户id列表返回以指定符号分隔的用户名字符串
async def getUserName(delimiter,users):
	userids = []
	result = []
	for userid in users:
		userids.append(int(userid))
	filters = {User.id.in_(userids)}
	allUser = User.getAll(*filters)
	for user in allUser:
		result.append(user['name'])
	logging.info('result: %s' % result)
	return delimiter.join(result)



@get('/manage/inspectionitem')
async def inspectionItem(request):
	return {
		'__template__': 'inspectionitem.html'
	}

@get('/api/gettype')
async def getInsType():

	types = InspectionType.getTypes()
	
	return dict(types=types)

@post('/api/addinspectionitem')
async def addItem(*, content, criterion, type_code, itemrequired=1):

	pass

# @get('/api/synmongodb')
# def syndata(*, epgdata):
# 	try:
# 		d = int(epgdata)
# 		logging.info('syn epgdata success')
# 	except Exception as e:
# 		logging.error('failed syn epgdata: parse epg template error - %s' % (e))
# 		logging.error('abort syn progress...')

@get('/manage/opttool')
async def getOptTool(request):
	return {
		'__template__': 'opttool.html'
	}

@get('/trouble/dashboard')
async def getDashboard(request):
	return {
		'__template__': 'dashboard.html'
	}
@get('/trouble/tickets')
async def getTroubleTickets(request):
	return {
		'__template__': 'tickets.html'
	}

@get('/trouble/contact')
async def getContact(request):
	return {
		'__template__': 'contact.html'
	}

@get('/trouble/wiki')
async def getWiki(request):
	return {
		'__template__': 'wiki.html'
	}

@post('/api/addtroubleticket')
async def addTroubleTicket(*, report_channel, type, region, level, description, 
		impact, startTime, custid, mac, contact, contact_phone, 
		create_user, create_user_name, deal_user, deal_user_name, attachments):

	return trouble.addTroubleTicket(report_channel, type, region, level, description, 
		impact, startTime, custid, mac, contact, contact_phone, 
		create_user, create_user_name, deal_user, deal_user_name, attachments)

@post('/api/updatetroubleticket')
async def updateTroubleTicket(*, tid, report_channel, type, region, level, description, 
		impact, custid, mac, contact, contact_phone, 
		deal_user, deal_user_name):
	return trouble.updateTroubleTicket(tid,report_channel, type, region, level, description, 
		impact, custid, mac, contact, contact_phone, 
		deal_user, deal_user_name)

@get('/api/troubleticket/gettrouble')
async def getTrouble(*, page, items_perpage, status, filterflag='',stime='', etime='', region='', level='', confirmedtype=''):
	page = int(page)
	items_perpage = int(items_perpage)
	if(filterflag != '' and int(filterflag) == 1):
		troubleCount = trouble.getAllTroubleCount(status, filterflag=True, stime=stime, 
			etime=etime, region=region, level=level, confirmedType=confirmedtype)
		troubles = trouble.getTroublePageByStatus(page, items_perpage, status, 
			filterflag=True, stime=stime, etime=etime, region=region, level=level, confirmedType=confirmedtype)
	else:
		troubleCount = trouble.getAllTroubleCount(status)
		troubles = trouble.getTroublePageByStatus(page, items_perpage, status) 
	totalPages = math.ceil(troubleCount / items_perpage)

	return dict(totalitems=troubleCount, totalpage=totalPages, troubles=troubles)


# 获取工单统计数据，uid为登录用户id，pid为厂商id(suppor_provider)
@get('/api/toubleticket/statistic')
async def getTroubleStat(*, uid, pid):
	#工单量
	troubleCount = trouble.getAllTroubleCount(const.STATUS_ALL)
	#待处理工单量
	acptTroubleCount = trouble.getAllTroubleCount(const.STATUS_ACCEPT)
	#处理中的工单
	dealingTroubleCount = trouble.getAllTroubleCount(const.STATUS_DEALING)
	#当前厂商待处理任务量
	taskCount = trouble.getTaskCountByProvider(pid)

	return dict(troubleCount=troubleCount, acptTroubleCount=acptTroubleCount, dealingTroubleCount=dealingTroubleCount,
		taskCount=taskCount)

@get('/api/toubleticket/gettask')
async def getTask(*, page, items_perpage, uid, pid):
	page = int(page)
	items_perpage = int(items_perpage)
	taskCount = trouble.getTaskCountByProvider(pid)
	totalPages = math.ceil(taskCount / items_perpage)
	tasks = trouble.getTaskPage(page, items_perpage, pid)

	return dict(totalitems=taskCount, totalpage=totalPages, tasks=tasks)

@get('/api/troubleticket/getlogs')
async def getLogsByTrouble(*, troubleid):
	return dict(logs=trouble.getDealLogByTrouble(troubleid))

@get('/api/troubleticket/getprovider')
async def getProvider():
	return dict(providers=trouble.getProvider())

#任务处理接口
@post('/api/troubleticket/dealingtask')
async def dealingTask(*,dealingtype, taskid, nextprovider, reply, confirmedtype,uid):
	
	# dealingtype： REPLY-回单， TRANSIT- 转派, FINISHED-结单
	# taskid -工单ID
	# nextprovider-下个处理厂家
	# reply - 工单处理备注

	return trouble.dealingTask(dealingtype, taskid, nextprovider, reply, confirmedtype, uid)

#工单直接处理接口
@post('/api/troubleticket/dealingtrouble')
async def dealingTrouble(*,troubleid, dealingtype, nextprovider, reply, uid):
	
	# dealingtype： TRANSIT- 转派, FINISHED-结单
	# nextprovider-下个处理厂家
	# reply - 工单处理备注

	return trouble.dealingTrouble(troubleid, dealingtype, nextprovider, reply, uid)

#工单直接处理接口
@post('/api/troubleticket/dealingtroublebatch')
async def dealingTroublebatch(*,troubles, dealingtype, nextprovider, reply, uid):
	
	# dealingtype： TRANSIT- 转派, FINISHED-结单
	# nextprovider-下个处理厂家
	# reply - 工单处理备注
	troubleList = troubles.split(',')
	res = dict()
	for troubleid in troubleList:
		res = trouble.dealingTrouble(troubleid, dealingtype, nextprovider, reply, uid)

	return res

@get('/api/troubleticket/gettroublecategory')
async def getTroubleCategory(*, categorytype):
	return dict(categories=trouble.getTroubleCategory(categorytype))

@get('/api/troubleticket/getimpactarea')
async def getImpactArea():
	return dict(areas=trouble.getImpactArea())

@get('/api/troubleticket/getregion')
async def getRegion():
	return dict(areas=trouble.getRegion())

# 上传知识库文件的处理函数
@post('/single-file')
async def uploadSingleFile(request):
	reader = await request.multipart()
	attachmentId = 0
	uid = 0
	# /!\ Don't forget to validate your inputs /!\

	# reader.next() will `yield` the fields of your form
	while True:
		field = await reader.next()	
		if field is None:
			logging.info('没找到可上传文件!')
			break 
		elif field.name == 'ufile':
			# assert field.name == 'ufile'
			# 生成随机名称，扩展名保持不变
			filename = field.filename
			storedUrl = str(uuid1())
			# You cannot rely on Content-Length if transfer is chunked.
			size = 0
			with open(os.path.join(os.getcwd(),'files', storedUrl), 'wb') as f:
				while True:
					chunk = await field.read_chunk()  # 8192 bytes by default.
					if not chunk:
						break
					size += len(chunk)
					f.write(chunk)
			attachmentId = trouble.addAttachment(uid, storedUrl, '', filename, size)
		elif field.name == 'uid':
			uid = await field.text()
			logging.info('uid: %s' % uid)
		
		
	if attachmentId == 0:
		raise APIValueError('attachment','附件上传失败')
	else:
		return dict(returncode=const.RETURN_OK, message='附件上传成功', id=attachmentId,filename=filename, url=storedUrl, size=size)


	
@post('/multiple-files')
async def uploadMultiFiles(request):
	reader = await request.multipart()

	# /!\ Don't forget to validate your inputs /!\

	# reader.next() will `yield` the fields of your form
	allFiles = []
	uid = 0
	while True:
		field = await reader.next()	
		if field is None:
			logging.info('没找到可上传文件!')
			break
		elif field.name == 'uid':
			uid = await field.text()
			logging.info('uid: %s' % uid)
		elif field.name.startswith('files'):
			logging.info('field: %s' % field.name)
			# 生成随机名称，扩展名保持不变
			filename = field.filename
			storedUrl = str(uuid1())
			# You cannot rely on Content-Length if transfer is chunked.
			size = 0
			with open(os.path.join(os.getcwd(),'files', storedUrl), 'wb') as f:
				while True:
					chunk = await field.read_chunk()  # 8192 bytes by default.
					if not chunk:
						break
					size += len(chunk)
					f.write(chunk)
			attId = trouble.addAttachment(uid, storedUrl, '', filename, size)
			allFiles.append(dict(id=attId,filename=filename,url=storedUrl,size=size))
			
	if len(allFiles) == 0:
		raise APIValueError('attachment','附件上传失败')
	else:
		return dict(returncode=const.RETURN_OK, message='附件上传成功', files=allFiles)


@streamer
async def file_sender(writer, file_path=None):
    """
    This function will read large file chunk by chunk and send it through HTTP
    without reading them into memory
    """
    with open(file_path, 'rb') as f:
        chunk = f.read(2 ** 16)
        while chunk:
            await writer.write(chunk)
            chunk = f.read(2 ** 16)

# 下载指定文件名的附件
# file_name 文件存储路径-uuid
# name 文件的显示名称
@get('/download/{file_name}')
async def download_file(file_name,request,*,name):
    # file_name = request.match_info['file_name']  # Could be a HUGE file
    headers = {
        "Content-disposition": "attachment; filename={name}".format(name=name)
    }

    file_path = os.path.join(os.getcwd(),'files', file_name)

    if not os.path.exists(file_path):
        return web.Response(
            body='File <{file_name}> does not exist'.format(file_name=file_name),
            status=404
        )

    return web.Response(
        body=file_sender(file_path=file_path),
        headers=headers
    )

@post('/addtag')
async def addTag(*,tagname):
	tagId = 0
	if not tagname or not tagname.strip():
		raise APIValueError('tag','标签名不能为空')
	filters = {Tag.name == tagname}
	if len(trouble.getAllTags(*filters)) > 0:
		raise APIError('tag', '标签已经存在')
	tagId = trouble.addTag(tagname)
	res = dict()
	res['returncode'] = const.RETURN_OK
	res['message'] = '用户添加成功'
	return res

@get('/tags')
async def getAllTags():
	return dict(tags=trouble.getAllTags())

@post('/addwiki')
async def addWiki(request, *, subject, summary, tags, attachment):
	logging.info("登录用户: %s - %s" % (request.__user__['id'], request.__user__['name']))
	logging.info("标签: %s" % str(tags))
	if not subject or not subject.strip():
		raise APIValueError('wiki','案例标题不能为空')
	if not summary or not summary.strip():
		raise APIValueError('wiki','案例概述不能为空')
	if len(tags) <=0:
		raise APIValueError('wiki', '请至少包含一个标签')
	if not attachment or int(attachment) <=0:
		raise APIValueError('wiki', '案例附件上传不正确')

	return trouble.addWiki(request.__user__['id'], request.__user__['name'],
		subject, summary, tags, attachment)

@get('/api/getwiki')
async def getWikiData(*, page, items_perpage, tag=''):
	page = int(page)
	items_perpage = int(items_perpage)
	if tag:
		wikiCount = trouble.getWikiCount(tag=tag)
		wikis = trouble.getWikiPage(page, items_perpage, tag=tag) 
	else:
		wikiCount = trouble.getWikiCount()
		wikis = trouble.getWikiPage(page, items_perpage) 
	totalPages = math.ceil(wikiCount / items_perpage)

	return dict(totalitems=wikiCount, totalpage=totalPages, wikis=wikis)





