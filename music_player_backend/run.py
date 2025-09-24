from app import create_app

app = create_app()

if __name__ == "__main__":
    # Note: For production, use a WSGI server. This is for development only.
    app.run(host="0.0.0.0", port=3001, debug=True)
