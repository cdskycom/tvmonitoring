# -*- coding: utf-8 -*-
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from orm import User, SupportProvider, TroubleTask, TroubleTicket, TroubleDealLog

class SupportProviderSchema(ModelSchema):
	class Meta:
		model = SupportProvider
		dateformat = '%Y-%m-%dT%H:%M:%S'
	# users = fields.Nested(UserSchema, many=True)

class UserSchema(ModelSchema):
	class Meta:
		model = User
		dateformat = '%Y-%m-%dT%H:%M:%S'
	support_provider = fields.Nested(SupportProviderSchema)

class TroubleTicketSchema(ModelSchema):
	class Meta:
		model = TroubleTicket
		dateformat = '%Y-%m-%dT%H:%M:%S'

class TroubleTaskSchema(ModelSchema):
	class Meta:
		model = TroubleTask
		dateformat = '%Y-%m-%dT%H:%M:%S'
	trouble = fields.Nested(TroubleTicketSchema)
	assigner = fields.Nested(UserSchema,exclude=('password',))

class TroubleDealLogSchema(ModelSchema):
	class Meta:
		model = TroubleDealLog
		dateformat = '%Y-%m-%dT%H:%M:%S'
	next_provider = fields.Nested(SupportProviderSchema)
