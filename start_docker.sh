#!/bin/sh

docker run -d --gpus all --shm-size 10G --rm --name toloka_video_processing_v2_container \
-p 127.0.0.1:8902:80 \
toloka_video_processing_v2
