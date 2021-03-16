from aws_cdk import core
import boto3
from iot_policy.iot_policy_resource_async import IotPolicyResourceAsync
from iot_policy.iot_policy_resource import IotPolicyResource

class CdkCustomResourceExampleStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        region = boto3.session.Session().region_name
        account_id = boto3.client('sts').get_caller_identity().get('Account')

        policy_document = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": "iot:Publish",
                    "Resource": f"arn:aws:iot:{region}:{account_id}:topic/some-topic"
                }]
            }

        IotPolicyResource(scope=self, id="IotPolicy1", policy_name="iot-policy-1", policy_document=policy_document)

        IotPolicyResourceAsync(scope=self, id="IotPolicyAsync1", policy_name="iot-policy-async-1", policy_document=policy_document)