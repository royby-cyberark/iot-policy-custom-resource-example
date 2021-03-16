import boto3

client = boto3.client('iot')

# This is just an example, IoT policy is quick to deploy and doesn't require this wait mechanism
def is_complete(event, context):
    physical_id = event["PhysicalResourceId"]
    print(event)
    is_ready = False

    request_type = event['RequestType'].lower()
    props = event['ResourceProperties']
    policy_name=props['policy_name']
    
    if request_type == 'create':
        try: 
            client.get_policy(policyName=policy_name)
            is_ready = True
        except client.exceptions.ResourceNotFoundException:
            is_ready = False
    if request_type == 'update':
        # Implement update wait logic here using the data in event['OldResourceProperties']
        is_ready = True
    if request_type == 'delete':
        try: 
            client.get_policy(policyName=policy_name)
            is_ready = False
        except client.exceptions.ResourceNotFoundException:
            is_ready = True
        
    return { 'IsComplete': is_ready }


