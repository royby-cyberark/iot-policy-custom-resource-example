import json
from os import path
from typing import Any

from aws_cdk import core
from aws_cdk.core import Duration, RemovalPolicy, Stack
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_iam as iam

from aws_cdk.custom_resources import Provider


class IotPolicyResource(core.Construct):
    """AWS IoT Policy construct
    Since using CfnIotPolicy has an issue where it can't update itself, we can use custom resources to work around this issue.
    This is because of the IoT Policy versioning and the unique name of the policy. 
    There is the issue: 
    https://github.com/aws-cloudformation/aws-cloudformation-coverage-roadmap/issues/469

    Arguments:
        :param policy_name - The IoT Policy name which needs to be unique in the account
        :param policy_document - the IoT Policy document, either a json object (Dict) or a string json
        :param timeout: The timeout for the Lambda function implementing this custom resource. Default: Duration.minutes(5)
    """

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        policy_name: str,
        policy_document: Any,
        timeout: Duration = None
    ) -> None:
        super().__init__(scope, id)

        if type(policy_document) == dict:
            policy_document = json.dumps(policy_document)

        account_id = Stack.of(self).account
        region = Stack.of(self).region

        lambda_role = iam.Role(
            scope=self,
            id=f'{id}LambdaRole',
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies={
                "IotPolicyProvisioningPolicy":
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(
                            actions=[
                                "iot:ListPolicyVersions", "iot:CreatePolicy", "iot:CreatePolicyVersion", "iot:DeletePolicy",
                                "iot:DeletePolicyVersion"
                            ],
                            resources=[f'arn:aws:iot:{region}:{account_id}:policy/{policy_name}'],
                            effect=iam.Effect.ALLOW,
                        )
                    ])
            },
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")],
        )

        if not timeout:
            timeout = Duration.minutes(5)

        with open(path.join(path.dirname(__file__), 'iot_policy_event_handler.py')) as file:
            code = file.read()

        event_handler = aws_lambda.Function(
            scope=self,
            id=f'{id}EventHandler',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_inline(code),
            handler='index.on_event',
            role=lambda_role,
            timeout=timeout,
        )

        provider = Provider(scope=self, id=f'{id}Provider', on_event_handler=event_handler)

        core.CustomResource(
            scope=self,
            id=f'{id}IotPolicy',
            service_token=provider.service_token,
            removal_policy=RemovalPolicy.DESTROY,
            resource_type="Custom::IotPolicy",
            properties={
                "policy_name": policy_name,
                "policy_document": policy_document,
            },
        )
