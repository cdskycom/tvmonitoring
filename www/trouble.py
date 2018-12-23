# -*- coding: utf-8 -*-

from orm import User, SupportProvider, TroubleTicket, TroubleDealLog, TroubleTask, SupportProvider, session_scope
from orm import TroubleCategory, ImpactArea, Region, Attachment, Tag, Wiki, wiki_tag, trouble_attachment
from const import const
import logging, time, datetime
from apis import APIValueError, APIError
from sqlalchemy.exc import IntegrityError

import pdb



def addTroubleTicket(report_channel, type, region, level, description, 
		impact, startTime, custid, mac, contact, contact_phone, 
		create_user, create_user_name, deal_user, deal_user_name, attachments):
	logging.info('创建工单，创建人: %s' % create_user_name)
	if not report_channel or not report_channel.strip():
		raise APIValueError('report_channel','上报渠道不能为空')
	if not type or not type.strip():
		raise APIValueError('trouble_type','故障类型不能为空')
	if not region or not region.strip():
		raise APIValueError('region','故障地市不能为空')
	if not level or not level.strip():
		raise APIValueError('level','故障级别不能为空')
	if not description or not description.strip():
		raise APIValueError('description', '故障现象不能为空')
	if not contact or not contact.strip():
		raise APIValueError('contact','故障联系人不能为空')
	if not create_user: 
		raise APIValueError('create_user', '工单创建人不能为空')	
	if not deal_user: 
		raise APIValueError('deal_user', '当前故障处理人不能为空')
	
	try:
		# 解析故障开始时间字符串到datetime对象
		st = datetime.datetime.strptime(startTime, '%Y-%m-%dT%H:%M')
	except Exception as e:
		raise APIValueError('datetime','故障日期格式不正确')
	
	with session_scope() as session:
		troubleTicket = TroubleTicket(report_channel, type, region, level, description, 
			impact, startTime, custid, mac, contact, contact_phone, 
			create_user, create_user_name, deal_user, deal_user_name)
		#添加工单处理日志
		session.add(troubleTicket)
		session.flush()
		user = session.query(User).join(User.support_provider).filter(User.id==deal_user).one()
		dealingLog = addTroubleLog(user, troubleTicket.id, '', const.DEALING_CREATE, None)
		session.add(dealingLog)
		
		if len(attachments) > 0:
			for attachment in attachments:
				statement = trouble_attachment.insert().values(trouble_id=troubleTicket.id,attachment_id=attachment)
				session.execute(statement)
		session.commit()


	res = dict()
	res['returncode'] = const.RETURN_OK
	res['message'] = '故障工单添加成功'
	return res

def updateTroubleTicket(tid, report_channel, type, region, level, description, 
		impact, custid, mac, contact, contact_phone, 
		deal_user, deal_user_name):
	logging.info('修改工单，修改人: %s' % deal_user_name)
	if not report_channel or not report_channel.strip():
		raise APIValueError('report_channel','上报渠道不能为空')
	if not type or not type.strip():
		raise APIValueError('trouble_type','故障类型不能为空')
	if not region or not region.strip():
		raise APIValueError('region','故障地市不能为空')
	if not level or not level.strip():
		raise APIValueError('level','故障级别不能为空')
	if not description or not description.strip():
		raise APIValueError('description', '故障现象不能为空')
	if not contact or not contact.strip():
		raise APIValueError('contact','故障联系人不能为空')
	if not deal_user: 
		raise APIValueError('deal_user', '当前故障处理人不能为空')
	
	with session_scope() as session:
		ticket = session.query(TroubleTicket).filter('id=' + str(tid)).one()
		if not ticket:
			raise APIValueError('troubleticket', '工单号不存在')
		ticket.report_channel = report_channel
		ticket.type = type
		ticket.region = region
		ticket.level = level
		ticket.description = description
		ticket.impact = impact
		ticket.custid = custid
		ticket.mac = mac
		ticket.contact = contact
		ticket.contact_phone = contact_phone
		ticket.deal_user = deal_user
		ticket.deal_user_name = deal_user_name
		session.commit()

	res = dict()
	res['returncode'] = const.RETURN_OK
	res['message'] = '更新工单成功'
	return res

# 返回工单查询过滤字段
def getTroubleFilters(status, filterflag=False, stime='', etime='', region='', level='', confirmedType=''):
	filters = ()
	if status.upper() != const.STATUS_ALL:
		filters = filters + (TroubleTicket.status == status,)
	if filterflag:
		if(stime == ''):
			stime = '1970-1-1'
		if(etime == ''):
			etime = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=1),'%Y-%m-%d')
		else:
			# 结束日期+1 以在数据库查询比较日期时能包含当日数据
			etime = datetime.datetime.strftime(datetime.datetime.strptime(etime,'%Y-%m-%d') + datetime.timedelta(days=1),'%Y-%m-%d')
		filters = filters + (TroubleTicket.startTime > stime,)
		filters = filters + (TroubleTicket.startTime < etime,)
		if(region != ''):
			filters = filters + (TroubleTicket.region == region,)
		if(level != ''):
			filters = filters + (TroubleTicket.level == level,)
		if(confirmedType != ''):
			filters = filters + (TroubleTicket.confirmed_type == confirmedType,)
	return filters

def getAllTroubleCount(status, filterflag=False, stime='', etime='', region='', level='', confirmedType=''):
	filters = getTroubleFilters(status, filterflag, stime, etime, region, level, confirmedType)
	return TroubleTicket.getTroubleCount(*filters)

def getTroublePageByStatus(page, items_perpage, status, filterflag=False, stime='', etime='', region='', level='', confirmedType=''):
	filters = getTroubleFilters(status, filterflag, stime, etime, region, level, confirmedType)
	return TroubleTicket.getTroublePage(page, items_perpage, *filters)


def getTaskCountByProvider(providerID):
	filters = {TroubleTask.support_provider == providerID, TroubleTask.status != 1}
	return TroubleTask.getTaskCount(*filters)

def getTask(providerID):
	filters = {TroubleTask.support_provider == providerID, TroubleTask.status != 1}
	return TroubleTask.getTask(*filters)

def getTaskPage(page, items_perpage, providerID):
	filters = {TroubleTask.support_provider == providerID, TroubleTask.status != 1}
	return TroubleTask.getTaskPage(page, items_perpage, *filters)

def getDealLogByTrouble(troubleId):
	return TroubleDealLog.getDealLogByTrouble(troubleId)

def getProvider():
	return SupportProvider.getAll()

def dealingTrouble(troubleid, dealingtype, nextprovider, reply, uid):
	res = dict()
	#生成任务
	with session_scope() as session:
		try:
			if(dealingtype != const.DEALING_FINISHED):
				#生成下一个任务
				createtime = datetime.datetime.now()
				assign_user = uid
				newTask = TroubleTask(trouble_ticket=troubleid, support_provider=nextprovider,
					remark=reply, createtime=createtime, assign_user=assign_user, status=0)
				session.add(newTask)
			#添加工单处理记录
			user = session.query(User).join(User.support_provider).filter(User.id==uid).one()
			dealingLog = addTroubleLog(user, troubleid, reply, dealingtype, nextprovider)
			session.add(dealingLog)

			#更新工单状态
			
			troubleTicketStatus = ''
			trouble = session.query(TroubleTicket).filter(TroubleTicket.id==troubleid).one()

			if(dealingtype == const.DEALING_FINISHED):

				if not checkPermission(user.permission,'FIN'):
					raise APIError('结单失败', 'permission', '你没有该权限')
				troubleTicketStatus = const.STATUS_FINISHED
				trouble.endtime = datetime.datetime.now()
			else:
				troubleTicketStatus = const.STATUS_DEALING
			trouble.status = troubleTicketStatus
			trouble.deal_user = uid
			trouble.deal_user_name = user.name
			trouble.dealingtime = datetime.datetime.now()
			session.commit()
		except IntegrityError:
			raise APIError('处理失败', 'database', '转派厂家信息异常')
	res['returncode'] = const.RETURN_OK
	res['message'] = '任务工单处理成功' + dealingtype
	return res


# 工单处理
def  dealingTask(dealingtype, taskid, nextprovider, reply, confirmedtype, uid):
	res = dict()
	with session_scope() as session:
		try:
			user = session.query(User).join(User.support_provider).filter(User.id==uid).one()
			#更新当前工单，接单不添加流转记录，仅更新状态和接单时间
			task = session.query(TroubleTask).filter(TroubleTask.id==taskid).one()
			if(dealingtype == const.DEALING_ACCEPT):
				task.status = const.TASK_ACCEPTED
				task.accepttime = datetime.datetime.now()
			else:
				task.status = const.TASK_FINISHED
				task.reply = reply
				task.endtime = datetime.datetime.now()
				#添加工程单处理记录
				dealingLog = addTroubleLog(user, task.trouble.id, reply, dealingtype, nextprovider)
				session.add(dealingLog)
			
			#接单和完成任务均不生成下一个任务
			if(dealingtype != const.DEALING_FINISHED and dealingtype != const.DEALING_ACCEPT):
				#生成下一个任务
				trouble_ticket = task.trouble.id
				support_provider = nextprovider
				remark = reply
				createtime = datetime.datetime.now()
				assign_user = uid
				newTask = TroubleTask(trouble_ticket=trouble_ticket, support_provider=support_provider,
					remark=remark, createtime=createtime, assign_user=assign_user, status=0)
				session.add(newTask)
		
			#更新工单状态
			troubleTicketStatus = ''
			trouble = session.query(TroubleTicket).filter(TroubleTicket.id==task.trouble.id).one()

			if(dealingtype == const.DEALING_FINISHED):

				if not checkPermission(user.permission,'FIN'):
					raise APIError('结单失败', 'permission', '你没有该权限')
				troubleTicketStatus = const.STATUS_FINISHED
				trouble.endtime = datetime.datetime.now()
				if not confirmedtype or not confirmedtype.strip():
					session.rollback()
					raise APIValueError('confirmedtype','问题归类不能为空')
				else:
					trouble.confirmed_type = confirmedtype
			else:
				troubleTicketStatus = const.STATUS_DEALING
			trouble.status = troubleTicketStatus
			trouble.deal_user = uid
			trouble.deal_user_name = user.name
			trouble.dealingtime = datetime.datetime.now()
			session.commit()
		except IntegrityError:
			raise APIError('处理失败', 'database', '转派厂家信息异常')
	res['returncode'] = const.RETURN_OK
	res['message'] = '任务工单处理成功' + dealingtype
	return res

def addTroubleLog(user, troubleId, reply, dealingtype, nextprovider):
	
	deal_user_name = user.name
	support_provider_name = user.support_provider.provider_name
	trouble_ticket_id = troubleId
	deal_user = user.id
	log_type = dealingtype
	if(not nextprovider or int(nextprovider) < 1):
		nextprovider = None
	dealingLog = TroubleDealLog(trouble_ticket_id=trouble_ticket_id, deal_user=deal_user,remark=reply,
		log_type=log_type, deal_user_name=deal_user_name, support_provider_name=support_provider_name,
		createtime=datetime.datetime.now(),next_provider_id=nextprovider)
	return dealingLog

def getTroubleCategory(categoryType):
	return TroubleCategory.getCategory(categoryType)

def getImpactArea():
	return ImpactArea.getImpactArea()

def getRegion():
	return Region.getRegion()

# 通过用户或分组的权限字符串检查特定权限
def checkPermission(userPermission, needed):
	permissionlist = userPermission.split('|')
	return needed in permissionlist

def addAttachment(userId, uuid, docType, filename, size):
	attachementId = 0
	with session_scope() as session:
		attachment = Attachment(user_id=userId, uuid=uuid, doc_type=docType, filename=filename, size=size)
		session.add(attachment)
		session.commit()
		attachementId = attachment.id
	return attachementId

def addTag(tagName):
	tagId = 0
	with session_scope() as session:
		newTag = Tag(name=tagName)
		session.add(newTag)
		session.commit()
		tagId = newTag.id
	return tagId

def getAllTags(*filters):
	return Tag.getAll(*filters)

def addWiki(userid, username,
		subject, summary, tags, attachmentId):
	wikiId = 0
	res = dict()
	with session_scope() as session:
		wiki = Wiki(subject=subject, summary=summary, attachment=attachmentId, 
			create_time=datetime.datetime.now(), create_user=userid,
			create_user_name=username)
		session.add(wiki)
		session.commit()
		wikiId = wiki.id
		for tagid in tags:
			statement = wiki_tag.insert().values(wiki_id=wikiId,tag_id=tagid)
			session.execute(statement)
		session.commit()
	res['returncode'] = const.RETURN_OK
	res['message'] = '添加案例成功, 案例名称:' + subject 
	return res

def getWikiCount(tag=''):
	if tag != '':
		# filters = ()
		# filters = filters + (Wiki.tags == status,)
		return Wiki.getWikiCount(tag)
	else:
		return Wiki.getWikiCount()

def getWikiPage(page, items_perpage, tag=''):
	if tag != '':
		return Wiki.getWikiPage(page, items_perpage,tag)
	else:
		return Wiki.getWikiPage(page, items_perpage)




