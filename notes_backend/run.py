import os
from app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "3001"))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(host=host, port=port, debug=debug)
