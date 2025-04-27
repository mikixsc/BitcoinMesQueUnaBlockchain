import os
from network import app

PORT = int(os.getenv("PORT", 5000))

if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=PORT)


