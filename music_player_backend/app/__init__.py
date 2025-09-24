from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
from werkzeug.exceptions import HTTPException

# Import blueprints from routes
from .routes.health import blp as health_blp
from .routes.files import blp as files_blp
from .routes.playback import blp as playback_blp
from .routes.preferences import blp as preferences_blp


def create_app() -> Flask:
    """
    Create and configure the Flask application with Ocean Professional style API docs.

    - Enables CORS
    - Configures OpenAPI/Swagger UI
    - Registers blueprints for health, files, playback, preferences
    - Adds consistent JSON error handling
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # CORS for all routes (adjust origins as needed via environment variables later)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Ocean Professional themed API docs (flask-smorest)
    app.config["API_TITLE"] = "Harmony Music Player API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    # Swagger UI config with Ocean Professional theme accents
    app.config["API_SPEC_OPTIONS"] = {
        "info": {
            "description": (
                "A clean, modern API for managing music files, playback, and user preferences.\n\n"
                "Theme: Ocean Professional - Blue and Amber accents."
            ),
            "contact": {"name": "Harmony", "url": "https://example.com"},
        },
        "tags": [
            {"name": "Health", "description": "Service health and readiness"},
            {"name": "Files", "description": "Upload, list, delete, and stream music files"},
            {"name": "Playback", "description": "Playback control operations"},
            {"name": "Preferences", "description": "Save and retrieve user preferences"},
        ],
        "x-logo": {
            "url": "https://dummyimage.com/200x40/2563EB/ffffff&text=Harmony",
            "altText": "Harmony",
        },
    }

    api = Api(app)

    # Register blueprints
    api.register_blueprint(health_blp)
    api.register_blueprint(files_blp)
    api.register_blueprint(playback_blp)
    api.register_blueprint(preferences_blp)

    # Consistent JSON error handling
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        response = {
            "code": e.code,
            "status": e.name,
            "message": e.description,
            "errors": {},
        }
        return jsonify(response), e.code

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        response = {
            "code": 500,
            "status": "Internal Server Error",
            "message": str(e),
            "errors": {},
        }
        return jsonify(response), 500

    return app


# App instance for WSGI servers
app = create_app()
