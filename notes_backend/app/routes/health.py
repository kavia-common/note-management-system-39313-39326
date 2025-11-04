from flask_smorest import Blueprint
from flask.views import MethodView

# Name, import_name, url_prefix, description
blp = Blueprint("Health", "health", url_prefix="/", description="Health check route")


@blp.route("/")
class HealthCheck(MethodView):
    def get(self):
        return {"message": "Healthy"}
