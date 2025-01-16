#!/bin/bash

image=registry.cn-wulanchabu.aliyuncs.com/gouboyun-pub/node:22-alpine3.20
docker run -it --memory=4g --rm -v `pwd`:/code -w /code $image ash

# npm config set registry https://registry.npmmirror.com