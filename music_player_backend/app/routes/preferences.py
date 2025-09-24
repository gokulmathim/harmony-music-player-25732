from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields
from ..storage import get_preferences, save_preferences

blp = Blueprint("Preferences", "preferences", url_prefix="/api/preferences", description="Save and retrieve user preferences")


class PreferencesSchema(Schema):
    theme = fields.String(required=False, description="UI theme selection")
    volume = fields.Float(required=False, description="Default playback volume (0.0 - 1.0)")
    repeat = fields.Boolean(required=False, description="Repeat mode enabled")
    shuffle = fields.Boolean(required=False, description="Shuffle mode enabled")
    last_track_id = fields.String(required=False, description="Last played track id")


class PreferencesResponseSchema(Schema):
    user_id = fields.String(required=True, description="User identifier")
    preferences = fields.Nested(PreferencesSchema, required=True)


@blp.route("/<string:user_id>")
class UserPreferences(MethodView):
    """
    Retrieve or update user preferences by user_id.
    """

    @blp.response(200, PreferencesResponseSchema)
    def get(self, user_id: str):
        """
        summary: Get user preferences
        description: Retrieve preferences for a given user_id.
        tags:
          - Preferences
        """
        prefs = get_preferences(user_id)
        return {"user_id": user_id, "preferences": prefs}

    @blp.arguments(PreferencesSchema)
    @blp.response(200, PreferencesResponseSchema)
    def put(self, prefs, user_id: str):
        """
        summary: Set user preferences
        description: Save user preferences for a given user_id.
        tags:
          - Preferences
        """
        saved = save_preferences(user_id, prefs)
        return {"user_id": user_id, "preferences": saved}
