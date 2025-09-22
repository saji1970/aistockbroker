from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Serve static files from the build directory
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('build', path)):
        return send_from_directory('build', path)
    else:
        return send_from_directory('build', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
