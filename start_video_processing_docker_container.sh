#!/bin/sh

docker run -d --gpus all --shm-size 10G --rm --name toloka_video_processing_container \
-p 127.0.0.1:8901:80 \
-v "${PWD}/volumes/data:/home/researcher/data" \
-v "${PWD}/volumes/dataset_preparing:/home/researcher/dataset_preparing" \
-v "${PWD}/volumes/workdir:/home/researcher/workdir" \
-v "${PWD}/volumes/src:/home/researcher/src" \
toloka_video_processing
