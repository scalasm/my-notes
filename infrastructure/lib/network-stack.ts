// Copyright Mario Scalas 2021. All Rights Reserved.
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

    this.vpc = new ec2.Vpc(this, "vpc", {
      natGateways: 1
    })
  }
}