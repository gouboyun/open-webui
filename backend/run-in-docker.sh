#!/bin/bash

cd $(dirname $0)

# image=registry.cn-wulanchabu.aliyuncs.com/gouboyun-pub/python:3.11-slim-bookworm
image=registry.cn-wulanchabu.aliyuncs.com/gouboyun-pub/ai-openwebui:py-base


docker run -it --memory=4g --rm -v `pwd`:/app/backend/ -w /app/backend/ $image bash

# apt-get update
# cp sources.list /etc/apt/sources.list
# apt-get install -y --no-install-recommends git build-essential pandoc gcc netcat-openbsd curl jq && \
# apt-get install -y --no-install-recommends gcc python3-dev && \
# # for RAG OCR
# apt-get install -y --no-install-recommends ffmpeg libsm6 libxext6 && \
# # cleanup
# rm -rf /var/lib/apt/lists/*;

# pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
# pip install --no-cache-dir -r requirements.txt
