#!/bin/sh

docker build -t toloka_video_processing .
mkdir -p volumes/data
mkdir -p volumes/dataset_preparing
mkdir -p volumes/src
mkdir -p volumes/workdir
