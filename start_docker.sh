#!/bin/sh

docker run -d --gpus all --shm-size 10G --rm --name toloka_video_processing_v3_container \
-p 127.0.0.1:8903:80 \
toloka_video_processing_v3
