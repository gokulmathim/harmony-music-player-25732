from flask import send_file, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields
from pathlib import Path
from ..storage import save_music_file, list_tracks, delete_track, get_track_by_id

blp = Blueprint("Files", "files", url_prefix="/api/files", description="Upload, list, delete and stream music files")


class TrackSchema(Schema):
    id = fields.String(required=True, description="Track identifier (filename stem)")
    filename = fields.String(required=True, description="File name as stored")
    size = fields.Integer(required=True, description="File size in bytes")
    extension = fields.String(required=True, description="File extension")


class TrackListSchema(Schema):
    tracks = fields.List(fields.Nested(TrackSchema), required=True, description="List of available tracks")


class UploadResponseSchema(Schema):
    message = fields.String(required=True, description="Status message")
    track = fields.Nested(TrackSchema, required=True, description="Uploaded track metadata")


@blp.route("/")
class FilesCollection(MethodView):
    """
    Manage the files collection: list and upload tracks.
    """

    @blp.response(200, TrackListSchema)
    def get(self):
        """
        summary: List tracks
        description: Returns a list of available tracks.
        tags:
          - Files
        """
        return {"tracks": list_tracks()}

    @blp.arguments(Schema, location="files", as_kwargs=True)
    @blp.response(201, UploadResponseSchema)
    def post(self, **kwargs):
        """
        summary: Upload a track
        description: Upload a music file. Accepted extensions: .mp3, .wav, .ogg, .flac, .m4a
        tags:
          - Files
        requestBody:
          required: true
          content:
            multipart/form-data:
              schema:
                type: object
                properties:
                  file:
                    type: string
                    format: binary
        """
        file = request.files.get("file")
        if not file:
            abort(400, message="No file provided. Use 'file' field in multipart/form-data.")
        try:
            track = save_music_file(file)
        except ValueError as e:
            abort(400, message=str(e))
        return {"message": "Uploaded", "track": track}, 201


@blp.route("/<string:track_id>")
class FileItem(MethodView):
    """
    Retrieve or delete a specific track by id.
    """

    @blp.response(200, TrackSchema)
    def get(self, track_id: str):
        """
        summary: Get track metadata
        description: Retrieve metadata for a specific track by id.
        tags:
          - Files
        """
        track = get_track_by_id(track_id)
        if not track:
            abort(404, message="Track not found.")
        return track

    def delete(self, track_id: str):
        """
        summary: Delete track
        description: Delete a specific track by id.
        tags:
          - Files
        responses:
          200:
            description: Track deleted
        """
        ok = delete_track(track_id)
        if not ok:
            abort(404, message="Track not found.")
        return {"message": "Deleted", "id": track_id}


@blp.route("/stream/<string:track_id>")
class FileStream(MethodView):
    """
    Stream a specific track.
    """

    def get(self, track_id: str):
        """
        summary: Stream track
        description: Streams the audio file for the specified track. Suitable for HTML5 audio elements.
        tags:
          - Files
        responses:
          200:
            description: File stream
          404:
            description: Not found
        """
        track = get_track_by_id(track_id)
        if not track:
            abort(404, message="Track not found.")
        path = Path(track.get("path"))
        if not path.exists():
            abort(404, message="File missing on server.")
        # Use send_file to stream. Range requests not implemented here for brevity.
        return send_file(str(path), as_attachment=False, download_name=track.get("filename"))
