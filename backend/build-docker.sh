#!/bin/bash

cd $(dirname $0)

# org=registry.cn-wulanchabu.aliyuncs.com/gouboyun/ai-openwebui:py-base
target=registry.cn-wulanchabu.aliyuncs.com/gouboyun-pub/ai-openwebui:py-base

# docker buildx imagetools create --tag $target $org


docker buildx build -t $target --platform linux/amd64,linux/arm64 --push .
