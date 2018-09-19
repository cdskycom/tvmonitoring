# -*- coding: utf-8 -*-

from orm import TroubleTicket, TroubleDealLog, TroubleTask
from const import const
import logging, time, datetime


def addTroubleTicket(report_channel, type, region, level, description, 
		impact, startTime, custid, mac, contact, contact_phone, 
		create_user, create_user_name, deal_user, deal_user_name):
	logging.info('创建工单，创建人: %s' % create_user_name)
	if not report_channel or not account.strip():
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
	
	troubleTicket = TroubleTicket(report_channel, type, region, level, description, 
		impact, startTime, custid, mac, contact, contact_phone, 
		create_user, create_user_name, deal_user, deal_user_name)

	troubleTicket.save()
	res = dict()
	res['returncode'] = const.RETURN_OK
	res['message'] = '故障工单添加成功'
	return res

def getAllTroubleCount(status):
	filters = {}
	if status.upper() != const.STATUS_ALL:
		filters = {TroubleTicket.status == status}
	return TroubleTicket.getTroubleCount(*filters)

def getTaskCountByProvider(providerID):
	filters = {TroubleTask.support_provider == providerID}
	return TroubleTask.getTaskCount(*filters)