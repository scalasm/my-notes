# Welcome to My Notes!

This is a simple serverless notes keeper based on AWS stack!

This repository is organized in two places:
* [infrastructure](./infrastructure/) containing the CDK 2.x App which defines the AWS stack resources
* [lambda](./lambda/) containing the Python code for the business logic implementation

# Deploy

## Pre-requisites

Ensure you have your Docker daemon runnning (e.g., Docker for Desktop must be running :))

## Do login into your AWS environment

Note: here we use `--profile development` - feel free to adapt or skip according to your AWS environment. 

```
aws sso login --profile development
cdk-sso-sync development
```

Within the `infrastructure` folder, run CDK deploy command:
```
(lambda-sXTDgYc4) mario@scalasm-xps:~/src/my-notes/my-notes/infrastructure$ npm run cdk:deploy -- --profile development
```
