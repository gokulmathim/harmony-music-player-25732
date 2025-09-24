# Harmony Music Player - Backend

Flask-based backend providing RESTful endpoints to manage music files, control playback, handle user preferences, and stream audio files.

Docs (Swagger/OpenAPI): default served at /docs

Ocean Professional Style:
- Primary: #2563EB (Blue)
- Secondary/Accent: #F59E0B (Amber)
- Clean, modern, minimal docs styling with subtle accents.

Key Endpoints:
- Health
  - GET / : service health
- Files
  - GET /api/files/ : list tracks
  - POST /api/files/ : upload multipart/form-data file (field: file)
  - GET /api/files/{track_id} : track metadata
  - DELETE /api/files/{track_id} : delete track
  - GET /api/files/stream/{track_id} : stream audio
- Playback
  - GET /api/playback/state/{session_id} : current playback state
  - POST /api/playback/play/{session_id} : play
  - POST /api/playback/pause/{session_id} : pause
  - POST /api/playback/next/{session_id} : next
  - POST /api/playback/previous/{session_id} : previous
  - GET /api/playback/queue/{session_id} : get queue
  - PUT /api/playback/queue/{session_id} : set queue
- Preferences
  - GET /api/preferences/{user_id}
  - PUT /api/preferences/{user_id}

Run locally:
- python music_player_backend/run.py
- Server default: http://localhost:3001