# -*- coding: utf-8 -*-
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from orm import User, SupportProvider, TroubleTask, TroubleTicket, TroubleDealLog
from orm import TroubleCategory, ImpactArea, Region

class SupportProviderSchema(ModelSchema):
	class Meta:
		model = SupportProvider
		dateformat = '%Y-%m-%dT%H:%M:%S'

	users = fields.Nested('UserSchema', many=True, only=["account","name","phone","email"])

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

class TroubleCategorySchema(ModelSchema):
	class Meta:
		model = TroubleCategory

class ImpactAreaSchema(ModelSchema):
	class Meta:
		model = ImpactArea

class RegionSchema(ModelSchema):
	class Meta:
		model = Region

		
