
# CDK Custom Resource Example - IoT Policy as a Custom Resource

This is an example of create Custom Resources with CDK.
You have two options:
1. using CDK's AWSCustomResource - which is not covered in this example
2. using CDK's Custom Resources (with a Provider and CustomResource) - covered in this project

Very confusing, I know!
for more details see the following blog posts:

Part 1: https://medium.com/cyberark-engineering/custom-resources-with-aws-cdk-d9a8fad6b673
Part 2: <Link>

There are two examples here, one for synchronously creating a custom resource: IotPolicyResource
and an asynchronously - IotPolicyResourceAsync when the creating lambda will initiate the resource creation and return, and then another lambda
will be called periodically to check for completion.
IMPORTANT: This is only an example. There no reason to deploy IotPolicyResourceAsync asynchronously since policy deployment is quick. 
but you can use this an a blueprint for create other, long running resource deployments. 

If you are new to CDK, see the getting started guide:
https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html

A few command to get started:

make sure you have python installed

```
$ python3 -m venv .venv
```
or python, depends on your environment

activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Deploy this code:

```
$ cdk deploy
```
