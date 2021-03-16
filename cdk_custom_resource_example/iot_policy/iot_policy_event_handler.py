import boto3


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

    client = boto3.client('iot')
    response = client.create_policy(
        policyName=props['policy_name'],
        policyDocument=props['policy_document'],
    )
    print(f'Created policy {response=}')

    physical_id = f'CustomIotPolicy{props["policy_name"]}'
    return {'PhysicalResourceId': physical_id}


def delete_oldest_version(client, policy_name, policy_versions):
    non_default_versions = [ver for ver in policy_versions if not ver['isDefaultVersion']]
    oldest_version = min(non_default_versions, default=None, key=lambda version: version['versionId'])
    if oldest_version:
        client.delete_policy_version(policyName=policy_name, policyVersionId=oldest_version['versionId'])
        print(f'Deleted policy version {policy_name=}, versionId={oldest_version["versionId"]}')


def on_update(event):
    physical_id = event["PhysicalResourceId"]
    props = event["ResourceProperties"]

    policy_name = props['policy_name']
    client = boto3.client('iot')
    response = client.list_policy_versions(policyName=policy_name)
    policy_versions = response.get('policyVersions', [])
    if len(policy_versions) >= 5:
        delete_oldest_version(client, policy_name=policy_name, policy_versions=policy_versions)

    policy_document = props['policy_document']
    response = client.create_policy_version(policyName=policy_name, policyDocument=policy_document, setAsDefault=True)
    print(f'Updated iot policy, {physical_id=}, {response=}, {policy_document=}')


def on_delete(event):
    props = event["ResourceProperties"]

    policy_name = props['policy_name']
    client = boto3.client('iot')
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
