from flask import Flask, request
app = Flask(__name__)
from video_checker import VideoChecker


@app.route("/", methods=['POST'])
def process():
    if 'video' not in request.files:
        return 'No video file.'
    video = request.files['video']
    return video_checker.check(video)


if __name__ == "__main__":
    video_checker = VideoChecker()
    app.run(host='0.0.0.0', port=80)
