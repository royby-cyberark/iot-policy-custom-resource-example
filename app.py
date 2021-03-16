#!/usr/bin/env python3

from aws_cdk import core

from cdk_custom_resource_example.cdk_custom_resource_example_stack import CdkCustomResourceExampleStack


app = core.App()
CdkCustomResourceExampleStack(app, "cdk-custom-resource-example")

app.synth()
