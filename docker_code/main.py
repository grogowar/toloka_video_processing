from flask import Flask
from flask import request
app = Flask(__name__)


@app.route("/", methods=['POST'])
def process():
    if 'video' not in request.files:
        return 'No video file.'
    video = request.files['video']
    return video.read()[-20:]


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
