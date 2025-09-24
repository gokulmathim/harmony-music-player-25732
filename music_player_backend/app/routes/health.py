from flask_smorest import Blueprint
from flask.views import MethodView

# Health blueprint
blp = Blueprint("Health", "health", url_prefix="/", description="Service health and readiness endpoints")


@blp.route("/")
class HealthCheck(MethodView):
    """
    Health check endpoint to verify the service is running.
    """
    def get(self):
        """
        summary: Health check
        description: Returns a simple JSON response indicating the service is healthy.
        responses:
          200:
            description: Service is healthy
        tags:
          - Health
        """
        return {"message": "Healthy", "service": "Harmony Music Player API"}
