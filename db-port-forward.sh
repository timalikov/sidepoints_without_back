#!/bin/bash

EC2_INSTANCE_ID=$(aws ecs describe-container-instances --container-instances $(aws ecs list-container-instances --cluster sidekick | jq -r '.containerInstanceArns[0]') --cluster sidekick | jq -r '.containerInstances[0].ec2InstanceId')
aws ssm start-session \
    --target "$EC2_INSTANCE_ID" \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters '{"host":["sidekick-dev.cc5otbogv4ap.eu-central-1.rds.amazonaws.com"],"portNumber":["5432"], "localPortNumber":["55432"]}'
