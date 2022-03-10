// Copyright Mario Scalas 2021. All Rights Reserved.
// This file is licensed under the MIT License.
// License text available at https://opensource.org/licenses/MIT

import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as cdk from 'aws-cdk-lib';
import * as constructs from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { NetworkStack } from './network-stack';
import { AuthStack } from './auth-stack';
import { MyNotesApiStack } from './my-notes-api';

/**
 * My Notes application resource stack.
 */
export class MyNotesApplicationStack extends cdk.Stack {
  constructor(scope: constructs.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const networkStack = new NetworkStack(this, "network");

    const authStack = new AuthStack(this, "auth", {
      userPoolName: "MyNotes User Pool"
    });

    const myNotesApi = new MyNotesApiStack(this, "mynotes-api", {
      vpc: networkStack.vpc
    });
  }
}
