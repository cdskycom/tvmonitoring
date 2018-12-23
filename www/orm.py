# -*- coding: utf-8 -*-
import sys, logging, json, datetime
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship, sessionmaker, joinedload, subqueryload

from sqlalchemy import create_engine, text, Column, Integer, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.sql import text
from contextlib import contextmanager
from collections import Iterable
from const import const
import pdb


Base = declarative_base()
Session = sessionmaker()

def get_dbengine( **kw):
	logging.info('create database engine')
	user=kw['user']
	db=kw['db']
	host=kw.get('host','localhost')
	password=kw['password']
	charset=kw.get('charset', 'utf8')

	connstr = 'mysql+pymysql://%s:%s@%s/%s?charset=%s' % (user, password, host, db, charset)
	logging.info('connstr: %s' % connstr)

	global __engine 
	__engine = create_engine(connstr, pool_recycle=300, echo=True)
	Session.configure(bind=__engine)

@contextmanager
def session_scope():
	session = Session()
	try:
		yield session
		session.commit()
	except:
		session.rollback()
		raise
	finally: 
		session.close()

#上传的附件model
class Attachment(Base):
	__tablename__ = 'attachments'
	id = Column(Integer, primary_key=True)
	uuid = Column(String(50))
	doc_type = Column(String(45))
	filename = Column(String(255))
	size = Column(Integer)
	user_id = Column(Integer)

# 标签model
class Tag(Base):
	__tablename__ = 'tags'
	id = Column(Integer, primary_key=True)
	name = Column(String(45))

	@classmethod
	def getAll(self, *filters):
		result = []
		with session_scope() as session:
			tags = session.query(Tag).filter(*filters).all()
			for tag in tags:
				result.append(tag.to_dict())
		return result

	def to_dict(self):
		from schema import TagSchema
		tag_schema = TagSchema()
		return tag_schema.dump(self).data

wiki_tag = Table('wiki_tag', Base.metadata,
	Column('wiki_id', ForeignKey('wikis.id'), primary_key=True),
	Column('tag_id', ForeignKey('tags.id'), primary_key=True)
	)


# 案例model
class Wiki(Base):
	__tablename__ = 'wikis'
	id = Column(Integer, primary_key=True)
	subject = Column(String(255))
	summary = Column(String(255))
	attachment = Column(Integer, ForeignKey('attachments.id'))
	create_time = Column(DateTime)
	create_user = Column(Integer)
	create_user_name = Column(String(45))

	attachmentFile = relationship('Attachment')
	tags = relationship('Tag',
		secondary=wiki_tag)
	@classmethod
	def getAllWiki(self, *filters):
		result = []
		with session_scope() as session:
			wikis = session.query(Wiki).filters(*filters).all()
			for wiki in wikis:
				result.append(wikik.to_dict())
		return result
	@classmethod
	def getWikiCount(self, tag='', *filters):
		with session_scope() as session:
			
			if tag != '':
				
				# sql = ''' select count(*) from wikis as w left join wiki_tag  as wt on w.id = wt.wiki_id
				# where wt.tag_id = :tagid
				# '''
				# stmt = text(sql)
				# stmt = stmt.bindparams(tagid=tag)
				# conn = session.connection()
				wikiCount = session.query(Wiki).join(wiki_tag,Wiki.id==wiki_tag.c.wiki_id).filter(wiki_tag.c.tag_id==tag).count()
			
			else:
				wikiCount = session.query(Wiki).filter(*filters).count()
		return wikiCount

	@classmethod
	def getWikiPage(self, page, items_perpage, tag='', *filters):
		with session_scope() as session:
			
			offset = (page - 1) * items_perpage
			if tag != '':
				
				# statement = wiki_tag.select().with_only_columns([wiki_tag.c.wiki_id]).where('tag_id=' + tag)
				# wikiIds = session.execute(statement).fetchall()
				# filterById = []
				# for i in wikiIds:
				# 	filterById.append(i[0])
				# wikis = session.query(Wiki).filter(Wiki.id.in_(filterById)).order_by("create_time desc").limit(items_perpage).offset(offset)
				wikis = session.query(Wiki).join(wiki_tag,Wiki.id==wiki_tag.c.wiki_id).filter(wiki_tag.c.tag_id==tag).order_by("create_time desc").limit(items_perpage).offset(offset)
			else:
				wikis = session.query(Wiki).filter(*filters).order_by("create_time desc").limit(items_perpage).offset(offset)

			result = []

			for wiki in wikis:
				result.append(wiki.to_dict())
		return result

	

	def to_dict(self):
		from schema import WikiSchema
		wiki_schema = WikiSchema()
		return wiki_schema.dump(self).data


# 服务供应商model
class SupportProvider(Base):
	__tablename__ = 'support_provider'
	id = Column(Integer, primary_key=True)
	provider_name = Column(String(100))
	contact = Column(String(45))
	contact_phone = Column(String(45))

	users = relationship("User", back_populates="support_provider")
	@classmethod
	def getAll(self):
		with session_scope() as session:
			providers = session.query(SupportProvider).all()

			result = []
			for provider in providers:
				result.append(provider.to_dict())

		return result

	def to_dict(self):
		from schema import SupportProviderSchema
		sp_schema = SupportProviderSchema()
		return sp_schema.dump(self).data

# 用户model
class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	account = Column(String(50))
	password = Column(String(50))
	name = Column(String(100))
	is_admin = Column(Integer)
	support_provider_id = Column(Integer, ForeignKey('support_provider.id'))
	permission = Column(String(100))
	phone = Column(String(45))
	email = Column(String(45))
	support_provider = relationship("SupportProvider")

	def __init__(self, account, password, name, is_admin, support_provider_id, phone, email):
		self.account = account
		self.password = password
		self.name = name
		self.is_admin = is_admin
		self.support_provider_id = support_provider_id
		self.phone = phone
		self.email = email

	# 查询用户信息，支持提供字符串过滤参数(filter1, filter2 ...)
	@classmethod
	def getAll(self, *filters):
		'返回所有的用户'
		
		with session_scope() as session:

			#userCount = session.query(User).filter(*filters).count()
				
			users = session.query(User).options(joinedload(User.support_provider)).filter(*filters).all()
			result = []
			
			for user in users:
				result.append(user.to_dict())
			#result = query_to_dict(users)
		
		return result
	
	def to_dict(self):
		from schema import UserSchema
		user_schema = UserSchema()
		return user_schema.dump(self).data

	@classmethod
	def getUserCount(self, *filters):
		with session_scope() as session:

			userCount = session.query(User).filter(*filters).count()
		
		return userCount

	@classmethod
	def getUserPage(self, page, items_perpage,*filters):
		with session_scope() as session:
			
			offset = (page - 1) * items_perpage
			users = session.query(User).filter(*filters).limit(items_perpage).offset(offset)
			result = []
			for user in users:
				result.append(user.to_dict())
			# result = query_to_dict(users)
		# for user in result:
		# 	user['password'] = '******'

		return result

	@classmethod
	def getUserById(self, id):
		
		with session_scope() as session:
			
			user = session.query(User).filter(User.id == id).one()
			# result = query_to_dict(user)
			result = user.to_dict()
		result['password'] = '******'
		return 	result
	
	@classmethod
	def updateUser(self, id, name, is_admin, phone, email):
		
		with session_scope() as session:
			
			user = session.query(User).filter(User.id == id).one()
			# logging.info('修改前的user： %s : %s : %s' % (user.account, user.name, user.password))
			user.name = name
			user.is_admin = is_admin
			user.phone = phone
			user.email = email
			
			session.commit()
			result = user.to_dict()
		return result	

	@classmethod
	def resetUser(self, id, password):
		
		with session_scope() as session:
			
			user = session.query(User).filter(User.id == id).one()
			logging.info('修改前的user： %s : %s : %s' % (user.account, user.name, user.password))
			logging.info('密码: %s' % password)
			user.password = password
			session.commit()
			result = user.to_dict()
		return result	

	@classmethod
	def deleteUser(self, id):
		
		with session_scope() as session:
			
			user = session.query(User).filter(User.id == id).one()
			
			session.delete(user)
		
		return True	
	
	def save(self):
		with session_scope() as session:
			session.add(self)
			session.commit()

	def __str__(self):
		return '<User(id: %s, account: %s, name: %s)>' % (self.id, self.account, self.name)

trouble_attachment = Table('trouble_attachment', Base.metadata,
	Column('trouble_id', ForeignKey('trouble_tickets.id'), primary_key=True),
	Column('attachment_id', ForeignKey('attachments.id'), primary_key=True)
	)


# 工单model
class TroubleTicket(Base):
	__tablename__ = 'trouble_tickets'

	id = Column(Integer, primary_key=True)
	#上报渠道
	report_channel = Column(String(45))
	#故障类型
	type = Column(String(45))
	region = Column(String(45))
	#故障级别 0-紧急故障、1-一般故障、2-感知问题
	level = Column(String(45))  
	description = Column(String(500))
	#故障影响
	impact = Column(String(500))
	startTime = Column(DateTime)
	endTime = Column(DateTime)
	custid = Column(String(15))
	mac = Column(String(17))
	contact = Column(String(45))
	contact_phone = Column(String(45))
	status = Column(String(20))
	create_user = Column(Integer, ForeignKey('users.id'))
	create_user_name = Column(String(45))
	deal_user = Column(Integer, ForeignKey('users.id'))
	deal_user_name = Column(String(45))
	dealingtime = Column(DateTime)
	confirmed_type = Column(String(45))

	tasks = relationship("TroubleTask", back_populates="trouble")
	attachments = relationship("Attachment", secondary=trouble_attachment)
	
	def __init__(self, report_channel, type, region, level, description, 
		impact, startTime, custid, mac, contact, contact_phone, 
		create_user, create_user_name, deal_user, deal_user_name):
		self.report_channel = report_channel
		self.type = type
		self.region = region
		self.level = level
		self.description = description
		self.impact = impact
		self.startTime = startTime
		self.custid = custid
		self.mac = mac
		self.contact = contact
		self.contact_phone = contact_phone
		self.status = const.STATUS_ACCEPT
		self.create_user = create_user
		self.create_user_name = create_user_name
		self.deal_user = deal_user
		self.deal_user_name = deal_user_name

	def save(self):
		with session_scope() as session:
			session.add(self)
			session.commit()

	@classmethod
	def getTroubleCount(self, *filters):
		with session_scope() as session:
			troubleCount = session.query(TroubleTicket).filter(*filters).count()
		
		return troubleCount

	@classmethod
	def getTroublePage(self, page, items_perpage, *filters):
		with session_scope() as session:
			
			offset = (page - 1) * items_perpage
			troubles = session.query(TroubleTicket).filter(*filters).order_by("startTime desc").limit(items_perpage).offset(offset)
			result = []
			for trouble in troubles:
				result.append(trouble.to_dict())
		return result

	def to_dict(self):
		from schema import TroubleTicketSchema
		trouble_schema = TroubleTicketSchema()
		return trouble_schema.dump(self).data



# 工单处理日志model
class TroubleDealLog(Base):
	__tablename__ = 'trouble_deal_log'

	id = Column(Integer, primary_key=True)
	trouble_ticket_id = Column(Integer, ForeignKey('trouble_tickets.id'))
	deal_user = Column(Integer, ForeignKey('users.id'))
	deal_user_name = Column(String(45))
	remark = Column(String(200))
	next_deal_user = Column(Integer, ForeignKey('users.id'))
	next_deal_user_name = Column(String(45))
	log_type = Column(String(45))
	support_provider_name = Column(String(45))
	createtime = Column(DateTime)
	next_provider_id = Column(Integer, ForeignKey('support_provider.id'))

	next_provider = relationship("SupportProvider")

	@classmethod
	def getDealLogByTrouble(self,troubleId):
		with session_scope() as session:
			logs = session.query(TroubleDealLog).filter(TroubleDealLog.trouble_ticket_id==troubleId).order_by(TroubleDealLog.createtime).all()
			result = []
			for log in logs:
				result.append(log.to_dict())
		return result

	def to_dict(self):
		from schema import TroubleDealLogSchema
		log_schema = TroubleDealLogSchema()
		return log_schema.dump(self).data

# 工单处理任务model
class TroubleTask(Base):
	__tablename__ = 'trouble_task'

	id = Column(Integer, primary_key=True)
	trouble_ticket = Column(Integer, ForeignKey('trouble_tickets.id'))
	# 任务状态 0-未处理、1-已完成、2-已接单未处理
	status = Column(Integer)
	support_provider = Column(Integer, ForeignKey('support_provider.id'))
	remark = Column(String(100))
	createtime = Column(DateTime)
	endtime = Column(DateTime)
	reply = Column(String(100))
	assign_user = Column(Integer, ForeignKey('users.id'))
	accepttime = Column(DateTime)

	trouble = relationship("TroubleTicket", back_populates="tasks")
	assigner = relationship("User")

	@classmethod
	def getTaskCount(self, *filters):
		with session_scope() as session:
			taskCount = session.query(TroubleTask).filter(*filters).count()
		
		return taskCount

	@classmethod
	def getTask(self, *filters):
		with session_scope() as session:
			tasks = session.query(TroubleTask).filter(*filters).order_by("createtime desc").all()
			result = []
			
			for task in tasks:
				result.append(task.to_dict())	
		return result

	@classmethod
	def getTaskPage(self, page, items_perpage, *filters):
		with session_scope() as session:
			
			offset = (page - 1) * items_perpage
			tasks = session.query(TroubleTask).filter(*filters).order_by("createtime desc").limit(items_perpage).offset(offset)
			result = []
			for task in tasks:
				
				result.append(task.to_dict())


		return result

	def to_dict(self):
		from schema import TroubleTaskSchema
		task_schema = TroubleTaskSchema()
		return task_schema.dump(self).data

	def __repr__(self):
		return "<Task(id='%s', createtime='%s')>" % (
			self.id, self.createtime)

# 故障类型
class TroubleCategory(Base):
	__tablename__ = 'trouble_category'
	id = Column(Integer, primary_key=True)
	name = Column(String(45))
	category_type = Column(String(4))

	@classmethod
	def getCategory(self,categoryType):
		with session_scope() as session:
			categories = session.query(TroubleCategory).filter_by(category_type=categoryType).all()
			result = []			
			for category in categories:
				result.append(category.to_dict())	
		return result

	def to_dict(self):
		from schema import TroubleCategorySchema
		category_schema = TroubleCategorySchema()
		return category_schema.dump(self).data

# 故障影响范围
class ImpactArea(Base):
	__tablename__ = 'impact_area'
	id = Column(Integer, primary_key=True)
	area = Column(String(45))

	@classmethod
	def getImpactArea(self):
		with session_scope() as session:
			areas = session.query(ImpactArea).all()
			result = []			
			for area in areas:
				result.append(area.to_dict())	
		return result

	def to_dict(self):
		from schema import ImpactAreaSchema
		area_schema = ImpactAreaSchema()
		return area_schema.dump(self).data

# 上报区域
class Region(Base):
	__tablename__ = 'region'
	id = Column(Integer, primary_key=True)
	region_code = Column(String(12))
	region_name = Column(String(45))

	@classmethod
	def getRegion(self):
		with session_scope() as session:
			regions = session.query(Region).all()
			result = []
			for region in regions:
				result.append(region.to_dict())
		return result

	def to_dict(self):
		from schema import RegionSchema
		region_schema = RegionSchema()
		return region_schema.dump(self).data


# 排班表
class Schedule(Base):
	__tablename__ = 'schedules'

	id = Column(Integer, primary_key=True)
	title = Column(String(50))
	startTime = Column(DateTime)
	endTime = Column(DateTime)
	users = Column(String(100)) #已排班的值班人员名字，竖线分隔
	shiftinfo = Column(Text) # 交班通知
	info_user = Column(Integer, ForeignKey('users.id'))
	info_username = Column(String(100))

	def __init__(self, title, startTime, endTime, users):
		self.title = title
		self.startTime = startTime
		self.endTime = endTime
		self.users = users

	def save(self):
		with session_scope() as session:
			session.add(self)
			session.commit()
			savedSchedule = query_to_dict(self)
		return  savedSchedule

	# 查询值班计划
	@classmethod
	def getAll(self, *filters):
		
		with session_scope() as session:
				
			schedules = session.query(Schedule).filter(*filters).all()
			
			result = query_to_dict(schedules)
		
		return result


	def __str__(self):
		return '<Schedule(id: %s, title: %s, startTime: %s, endTime: %s, users: %s)>' % (self.id, self.title, self.startTime, self.endTime, self.users)



# 值班表-记录用户登录的班次
class OnDuty(Base):
	__tablename__ = 'on_duty'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	schedule_id = Column(Integer, ForeignKey('schedules.id'))
	user_name = Column(String(100))
	schedule_title = Column(String(50))
	login_time = Column(DateTime)
	logout_time = Column(DateTime)
	

# 巡检类型与巡检项关系表映射
# type_items = Table('type_items', Base.metadata,
# 	Column('type_id', ForeignKey('inspection_type.id'), primary_key=True),
# 	Column('item_id', ForeignKey('inspection_items.id'), primary_key=True),
# 	# 是否必检
# 	Column('required', Integer))

class TypeItemAssociation(Base):
	__tablename__ = 'type_items'
	type_id = Column('type_id', ForeignKey('inspection_type.id'), primary_key=True)
	item_id = Column('item_id', ForeignKey('inspection_items.id'), primary_key=True)
	# 是否必检
	required = Column('required', Integer)
	item = relationship('InspectionItem')


# 巡检类别Model
class InspectionType(Base):
	__tablename__ = 'inspection_type'

	id = Column(Integer, primary_key=True)
	name = Column(String(100))
	code = Column(String(10))
	desc = Column(Text(200))
	created_at = Column(DateTime)
	updated_at = Column(DateTime)

	type_items =  relationship('TypeItemAssociation')

	@classmethod
	def getItemsByCode(self, code):
		with session_scope() as session:
			items = session.query(InspectionType).join('type_items', 'item').filter(InspectionType.code==code)
			result = query_to_dict(items)
		return result

	@classmethod
	def getTypes(self):
		with session_scope() as session:
			types = session.query(InspectionType.code, InspectionType.name, InspectionType.desc).all()
			result = query_to_dict(types)

		return result

	def __str__(self):
		return '<InspectionType(id: %s, name: %s, code: %s, desc: %s)>' % (self.id, self.name, self.code, self.desc)


class InspectionItem(Base):
	__tablename__ = 'inspection_items'
	id = Column(Integer, primary_key=True)
	content = Column(String(200))
	criterion = Column(String(200))
	


	def __init__(self,content, criterion):
		self.content = content
		self.criterion = criterion
		

	def save(self,type_code, itemrequired):
		with session_scope() as session:
			insType = session.query(InspectionType).filter(InspectionType.code==type_code).one()
			assoc = TypeItemAssociation(required = itemrequired)
			assoc.item = self
			insType.type_items.append(assoc)
			session.add(insType)
			items = query_to_dict(self)
		return items

	@classmethod
	def getItems(self,*filters):
		with session_scope() as session:
			items = session.query(InspectionItem).filter(*filters).all()
			for item in items:
				item.type_list = session.query(InspectionType.code,InspectionType.name).filter(
					TypeItemAssociation.item_id==item.id).filter(TypeItemAssociation.type_id==InspectionType.id).all()
			result =query_to_dict(items)
		return result


	def __str__(self):
		return '<InspectionItem(id: %s, content: %s, criterion: %s)>' % (self.id, self.content, self.criterion)


# 巡检明细表
class InspectionDetail(Base):
	__tablename__ = 'inspection_detail'

	id = Column(Integer, primary_key=True)
	item_id = Column(Integer, ForeignKey('inspection_items.id'))
	status = Column(String(10)) #ok/error/unexecuted
	info = Column(Text)
	time = Column(DateTime)
	created_at = Column(DateTime)
	updated_at = Column(DateTime)
	update_user = Column(String(100))
	inspection_id = Column(Integer, ForeignKey('inspections.id'))

	# inspection = relationship('Inspection', back_populates='inspected_items')

# 巡检记录表
class Inspection(Base):
	__tablename__ = 'inspections'

	id = Column(Integer, primary_key=True)
	time = Column(DateTime)
	user_id = Column(Integer, ForeignKey('users.id'))
	user_name = Column(String(100))
	schedule_id = Column(Integer)
	schedule_title = Column(String(50))
	inspections_count = Column(Integer)
	problems_count = Column(Integer)
	created_at = Column(DateTime)
	updated_at = Column(DateTime)
	status = Column(String(50))  #initial-任务初始状态；processing-已提交巡检，问题跟进中，问题未处理完；compeleted-巡检完成并归口
	type_code = Column(String(20),ForeignKey('inspection_type.code')) #巡检类型code
	type_name = Column(String(50))
	
	inspection_type = relationship('InspectionType')

	inspected_items = relationship('InspectionDetail') # order_by=InspectionDetail.id, back_populates='inspection'

	def __init__(self, time, schedule_id, schedule_title, created_at, updated_at, type_code, type_name):
		self.time = time
		self.schedule_id = schedule_id
		self.schedule_title = schedule_title
		self.created_at = created_at
		self.updated_at = updated_at
		self.type_code = type_code
		self.type_name = type_name

	def save(self):
		with session_scope() as session:
			session.add(self)
			session.commit()
			savedInspection = query_to_dict(self)
		return  savedInspection

	@classmethod
	def getAll(self):
		'返回所有的巡检记录'
		with session_scope() as session:
			# options(joinedload(Inspection.inspected_items))
			inspections = session.query(Inspection).options(subqueryload(Inspection.inspected_items)).all()
			
			result = query_to_dict(inspections)
		return result

	def __str__(self):
		return '<Inspection(id: %s  schedule_title: %s)>' % (self.id, self.schedule_title)

# 将查询结果集转换为dict，以返回前端接口
def query_to_dict(obj):
	if isinstance(obj, Iterable):
		return [orm_to_dict(item) for item in obj]
	else:
		return orm_to_dict(obj)
	
# ORM对象转换为字典对象
def orm_to_dict(obj):
	if isinstance(obj.__class__, DeclarativeMeta):

			# an SQLAlchemy class
			fields = {}
			for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and hasattr(obj.__getattribute__(x), '__call__') == False]:
				data = obj.__getattribute__(field)
				try:
					json.dumps(data)     # this will fail on non-encodable values, like other classes
					fields[field] = data

				except TypeError:    # 添加了对datetime的处理
					if isinstance(data, datetime.datetime):
						fields[field] = data.isoformat()
					elif isinstance(data, datetime.date):
						fields[field] = data.isoformat()
					elif isinstance(data, datetime.timedelta):
						fields[field] = (datetime.datetime.min + data).time().isoformat()
					elif isinstance(data, Iterable):

						fields[field] = [ orm_to_dict(item) for item in data]
					elif isinstance(data.__class__, DeclarativeMeta):
						fields[field] = orm_to_dict(data)
					else:
						fields[field] = None
			# a json-encodable dict
			return fields
	return obj


# 创建数据库-初始化数据
def create_db():
	try:
		logging.info('create db schema...')
		Base.metadata.create_all(__engine)
		logging.info('create db success')
	except Exception as e:
		logging.info('create db failed: %s' % e)

if __name__ == '__main__':
	from config import configs
	get_dbengine(**configs.db)
	if len(sys.argv) > 1 and sys.argv[1] == '--createdb':
		print(sys.argv[1])
		create_db()
	# print(InspectionType.getTypes())
	

	print(InspectionItem.getItems())

