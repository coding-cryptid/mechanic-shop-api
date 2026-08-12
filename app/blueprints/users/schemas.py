from flask_marshmallow import Schema, fields, validate

from app.extensions import ma
from app.models import Users

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))