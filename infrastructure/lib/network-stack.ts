// Copyright Mario Scalas 2022. All Rights Reserved.
// This file is licensed under the MIT License.
// License text available at https://opensource.org/licenses/MIT

import { NestedStack, NestedStackProps } from "aws-cdk-lib";
import * as constructs from "constructs";
import * as ec2 from "aws-cdk-lib/aws-ec2";

/**
 * Network stack for hosting the application.
 */
export class NetworkStack extends NestedStack {

  readonly vpc: ec2.IVpc;

  constructor(scope: constructs.Construct, id: string, props?: NestedStackProps) {
    super(scope, id, props);

    // We only need private subnets for hosting our lambda functions
    // In this way, we can avoid the cot of the NAT Gateway
    this.vpc = new ec2.Vpc(this, "vpc", {
      cidr: "10.10.0.0/16",
      natGateways: 0,
      maxAzs: 3, // This is the default - but better to make it explicit, since we are creating the subnets too
      subnetConfiguration: [
        {
          name: 'private-subnet-1',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
          cidrMask: 24,
        },
        {
          name: 'private-subnet-2',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
          cidrMask: 24,
        },
        {
          name: 'private-subnet-3',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
          cidrMask: 24,
        }
      ]
    });

    // Since we only have private subnets, our lambdas cannot access Internet and, thus, no AWS services.
    // This is not problem - we use the VPC endpoints for AWS DynamoDB and S3, the services we use for data storage.
    this.vpc.addGatewayEndpoint('s3-endpoint', {
      service: ec2.GatewayVpcEndpointAwsService.S3
    });
    this.vpc.addGatewayEndpoint('dynamodb-endpoint', {
      service: ec2.GatewayVpcEndpointAwsService.DYNAMODB
    });
  }
}