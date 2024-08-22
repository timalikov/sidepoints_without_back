#!/bin/bash

TASK_ARN=$(aws ecs list-tasks --cluster sidekick --service-name sidekick-botapi2 | jq -r '.taskArns[0]')
CONTAINER_INSTANCE_ARN=$(aws ecs describe-tasks --cluster sidekick --tasks "$TASK_ARN" | jq -r '.tasks[0].containerInstanceArn')
EC2_INSTANCE_ID=$(aws ecs describe-container-instances --cluster sidekick --container-instances $CONTAINER_INSTANCE_ARN | jq -r '.containerInstances[0].ec2InstanceId')
SERVER_PORT=$(aws ecs describe-tasks --cluster sidekick --tasks "$TASK_ARN" | jq -r '.tasks[0].containers[] | select(.name=="sidekick-bot") .networkBindings[0].hostPort')
aws ssm start-session \
    --target "$EC2_INSTANCE_ID" \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters "{\"host\":[\"localhost\"],\"portNumber\":[\"$SERVER_PORT\"], \"localPortNumber\":[\"8080\"]}"
