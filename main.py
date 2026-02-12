"""
Solutions PM — Entry Point
Run: python main.py
"""
from server import app
import config

if __name__ == "__main__":
    print(f"\n  Solutions PM — Business Manager")
    print(f"  http://localhost:{config.PORT}\n")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
