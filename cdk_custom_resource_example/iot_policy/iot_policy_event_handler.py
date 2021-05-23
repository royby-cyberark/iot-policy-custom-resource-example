from typing import Any
import boto3


client = boto3.client('iot')
    

def on_event(event, context):
    print(event)
    request_type = event['RequestType'].lower()
    if request_type == 'create':
        return on_create(event)
    if request_type == 'update':
        return on_update(event)
    if request_type == 'delete':
        return on_delete(event)
    raise Exception(f'Invalid request type: {request_type}')


def on_create(event):
    props = event["ResourceProperties"]
    print(f'create new resource with {props=}')

    create_policy(policy_name=props['policy_name'], policy_document=props['policy_document'])
    physical_id = physical_id_from_policy_name(props["policy_name"])
    return {'PhysicalResourceId': physical_id}


def on_update(event):
    physical_id = event["PhysicalResourceId"]
    props = event["ResourceProperties"]
    old_props = event["OldResourceProperties"]
    print(f'update resource {physical_id} with {props=}, {old_props=}')

    policy_name = props['policy_name']
    old_policy_name = old_props['policy_name']
    if policy_name != old_policy_name:
        physical_id = physical_id_from_policy_name(policy_name)
        create_policy(policy_name=props['policy_name'], policy_document=props['policy_document'])
		

    response = client.list_policy_versions(policyName=policy_name)
    policy_versions = response.get('policyVersions', [])
    if len(policy_versions) >= 5:
        delete_oldest_version(client, policy_name=policy_name, policy_versions=policy_versions)

    policy_document = props['policy_document']
    response = client.create_policy_version(policyName=policy_name, policyDocument=policy_document, setAsDefault=True)
    print(f'Updated iot policy, {physical_id=}, {response=}, {policy_document=}')

    return {'PhysicalResourceId': physical_id}

def on_delete(event):
    physical_id = event["PhysicalResourceId"]
    props = event["ResourceProperties"]

    policy_name = props['policy_name']

    response = client.list_policy_versions(policyName=policy_name)
    for version in response.get('policyVersions'):
        if not version['isDefaultVersion']:
            version_id = version['versionId']
            print(f'Deleting policy version: {policy_name}.{version_id}')
            response = client.delete_policy_version(policyName=policy_name, policyVersionId=version_id)
            print(f'{response=}')
    print(f'Deleting policy {policy_name}')
    response = client.delete_policy(policyName=policy_name)
    print(f'{response=}')
    return {'PhysicalResourceId': physical_id}


def delete_oldest_version(client, policy_name, policy_versions):
    non_default_versions = [ver for ver in policy_versions if not ver['isDefaultVersion']]
    oldest_version = min(non_default_versions, default=None, key=lambda version: version['versionId'])
    if oldest_version:
        client.delete_policy_version(policyName=policy_name, policyVersionId=oldest_version['versionId'])
        print(f'Deleted policy version {policy_name=}, versionId={oldest_version["versionId"]}')

        
def physical_id_from_policy_name(policy_name: str) -> str:
    return f'CustomIotPolicy{policy_name}'

    
def create_policy(policy_name: str, policy_document: Any):
    response = client.create_policy(policyName=policy_name, policyDocument=policy_document)
    print(f'Created policy {response=}')
    