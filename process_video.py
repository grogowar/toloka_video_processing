#!/usr/bin/env python3

import argparse
import requests
import os
import sys


def process(video_file):
    file = open(video_file, 'rb')
    files = {'video': (video_file, file)}
    proxies = {'http': None, 'https': None}
    r = requests.post('http://127.0.0.1:8903/', files=files, proxies=proxies)
    file.close()
    return r.text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video_file", help="video file name")
    args = parser.parse_args()
    if not os.path.isfile(args.video_file):
        sys.exit('There is no such file: %s' % args.video_file)
    print(process(args.video_file))
