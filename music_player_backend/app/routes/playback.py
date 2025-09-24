from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields, validate
from typing import Dict, Any
from ..storage import list_tracks

blp = Blueprint("Playback", "playback", url_prefix="/api/playback", description="Playback control operations")


# Simple in-memory playback state per session key
# In production, replace with a persistent/session-aware store (e.g., Redis).
PLAYBACK_STATE: Dict[str, Dict[str, Any]] = {}


def _default_state() -> Dict[str, Any]:
    tracks = list_tracks()
    return {
        "queue": [t["id"] for t in tracks],
        "current_index": 0 if tracks else -1,
        "is_playing": False,
        "current_track": tracks[0]["id"] if tracks else None,
    }


def _get_state(session_id: str) -> Dict[str, Any]:
    if session_id not in PLAYBACK_STATE:
        PLAYBACK_STATE[session_id] = _default_state()
    return PLAYBACK_STATE[session_id]


class PlaybackStateSchema(Schema):
    session_id = fields.String(required=True, description="Playback session identifier")
    queue = fields.List(fields.String(), required=True, description="Queue of track ids")
    current_index = fields.Integer(required=True, description="Current index in the queue")
    is_playing = fields.Boolean(required=True, description="Is playback active")
    current_track = fields.String(allow_none=True, description="Current track id")


class SetQueueSchema(Schema):
    queue = fields.List(fields.String(), required=True, validate=validate.Length(min=1), description="New queue of track ids")


class SessionSchema(Schema):
    session_id = fields.String(required=True, description="Playback session identifier")


@blp.route("/state/<string:session_id>")
class PlaybackState(MethodView):
    """
    Get current playback state.
    """

    @blp.response(200, PlaybackStateSchema)
    def get(self, session_id: str):
        """
        summary: Get playback state
        description: Returns the current playback state for the given session.
        tags:
          - Playback
        """
        state = _get_state(session_id)
        return {"session_id": session_id, **state}


@blp.route("/play/<string:session_id>")
class PlaybackPlay(MethodView):
    """
    Start or resume playback.
    """

    @blp.response(200, PlaybackStateSchema)
    def post(self, session_id: str):
        """
        summary: Play
        description: Start or resume playback for a session.
        tags:
          - Playback
        """
        state = _get_state(session_id)
        if state["current_index"] == -1:
            abort(400, message="No tracks available to play.")
        state["is_playing"] = True
        return {"session_id": session_id, **state}


@blp.route("/pause/<string:session_id>")
class PlaybackPause(MethodView):
    """
    Pause playback.
    """

    @blp.response(200, PlaybackStateSchema)
    def post(self, session_id: str):
        """
        summary: Pause
        description: Pause playback for a session.
        tags:
          - Playback
        """
        state = _get_state(session_id)
        state["is_playing"] = False
        return {"session_id": session_id, **state}


@blp.route("/next/<string:session_id>")
class PlaybackNext(MethodView):
    """
    Move to next track in queue.
    """

    @blp.response(200, PlaybackStateSchema)
    def post(self, session_id: str):
        """
        summary: Next track
        description: Move to next track and set as current, continuing play state.
        tags:
          - Playback
        """
        state = _get_state(session_id)
        if not state["queue"]:
            abort(400, message="Queue is empty.")
        state["current_index"] = (state["current_index"] + 1) % len(state["queue"])
        state["current_track"] = state["queue"][state["current_index"]]
        return {"session_id": session_id, **state}


@blp.route("/previous/<string:session_id>")
class PlaybackPrevious(MethodView):
    """
    Move to previous track in queue.
    """

    @blp.response(200, PlaybackStateSchema)
    def post(self, session_id: str):
        """
        summary: Previous track
        description: Move to previous track and set as current, continuing play state.
        tags:
          - Playback
        """
        state = _get_state(session_id)
        if not state["queue"]:
            abort(400, message="Queue is empty.")
        state["current_index"] = (state["current_index"] - 1) % len(state["queue"])
        state["current_track"] = state["queue"][state["current_index"]]
        return {"session_id": session_id, **state}


@blp.route("/queue/<string:session_id>")
class PlaybackQueue(MethodView):
    """
    Get or set queue for a session.
    """

    @blp.response(200, SetQueueSchema)
    def get(self, session_id: str):
        """
        summary: Get queue
        description: Get the current queue for a session.
        tags:
          - Playback
        """
        state = _get_state(session_id)
        return {"queue": state["queue"]}

    @blp.arguments(SetQueueSchema)
    @blp.response(200, PlaybackStateSchema)
    def put(self, args, session_id: str):
        """
        summary: Set queue
        description: Replace existing queue with new queue and reset current index.
        tags:
          - Playback
        """
        state = _get_state(session_id)
        state["queue"] = list(args["queue"])
        state["current_index"] = 0 if state["queue"] else -1
        state["current_track"] = state["queue"][0] if state["queue"] else None
        return {"session_id": session_id, **state}
