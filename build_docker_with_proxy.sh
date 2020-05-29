#!/bin/sh

docker build -t toloka_video_processing_v2  --build-arg http_proxy=http://proxy2.stc:3128 \
 --build-arg https_proxy=http://proxy2.stc:3128 .
