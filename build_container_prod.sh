#!/bin/bash
docker build --platform linux/arm64 -t 104037811570.dkr.ecr.eu-central-1.amazonaws.com/discord-bot:prod . || exit
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 104037811570.dkr.ecr.eu-central-1.amazonaws.com || exit
docker push 104037811570.dkr.ecr.eu-central-1.amazonaws.com/discord-bot:prod || exit