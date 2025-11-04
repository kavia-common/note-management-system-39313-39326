from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
from .routes.health import blp as health_blp
from .routes.notes import blp as notes_blp

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})

# OpenAPI/Swagger configuration
app.config["API_TITLE"] = "Notes Management API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Tag metadata to group endpoints
app.config["OPENAPI_TAGS"] = [
    {"name": "Health", "description": "Health check route"},
    {"name": "Notes", "description": "CRUD operations for notes"},
]

api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(notes_blp)

# Basic JSON error handlers to ensure consistent error responses
@app.errorhandler(400)
def bad_request(err):
    return jsonify({"code": 400, "status": "Bad Request", "message": getattr(err, "description", str(err))}), 400

@app.errorhandler(404)
def not_found(err):
    return jsonify({"code": 404, "status": "Not Found", "message": getattr(err, "description", str(err))}), 404

@app.errorhandler(500)
def internal_error(err):
    return jsonify({"code": 500, "status": "Internal Server Error", "message": getattr(err, "description", str(err))}), 500
