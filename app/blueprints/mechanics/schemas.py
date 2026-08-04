from app.extensions import ma
from app.models import Mechanics

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics
        load_instance = True

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)