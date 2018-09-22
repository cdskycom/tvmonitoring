# -*- coding: utf-8 -*-
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from orm import User, SupportProvider, TroubleTask, TroubleTicket, TroubleDealLog

class SupportProviderSchema(ModelSchema):
	class Meta:
		model = SupportProvider
	# users = fields.Nested(UserSchema, many=True)

class UserSchema(ModelSchema):
	class Meta:
		model = User
	support_provider = fields.Nested(SupportProviderSchema)

class TroubleTicketSchema(ModelSchema):
	class Meta:
		model = TroubleTicket

class TroubleTaskSchema(ModelSchema):
	class Meta:
		model = TroubleTask
	trouble = fields.Nested(TroubleTicketSchema)
	assigner = fields.Nested(UserSchema,exclude=('password',))

class TroubleDealLogSchema(ModelSchema):
	class Meta:
		model = TroubleDealLog
