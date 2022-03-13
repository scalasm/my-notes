// Copyright Mario Scalas 2021. All Rights Reserved.
// This file is licensed under the MIT License.
// License text available at https://opensource.org/licenses/MIT

import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as cdk from 'aws-cdk-lib';
import * as constructs from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as pylambda from "@aws-cdk/aws-lambda-python-alpha";
import * as ddb from 'aws-cdk-lib/aws-dynamodb';

import path = require('path');

export interface MyNotesApiStackProps extends cdk.NestedStackProps {
  readonly vpc: ec2.IVpc;
}

/**
 * My Notes application resource stack.
 */
export class MyNotesApiStack extends cdk.NestedStack {
  constructor(scope: constructs.Construct, id: string, props: MyNotesApiStackProps) {
    super(scope, id, props);

    const notesTable = new ddb.Table(this, "NotesTable", {
      tableName: "Notes",
      billingMode: ddb.BillingMode.PAY_PER_REQUEST,
      partitionKey: {
        name: "id",
        type: ddb.AttributeType.STRING,
      },
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });

    const notesContentBucket = new s3.Bucket(this, 'NotesContentBucket', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED
    });

    const apiGateway = new apigw.RestApi(this, "note-api", {
      restApiName: "My Notes REST API",
      description: "API for managing notes",
      binaryMediaTypes: ["*/*"],
      minimumCompressionSize: 0
    });

    const noteResource = apiGateway
      .root
      .addResource("note");

    // GET /note/asset/{folder}/{key}
//    this.setUpGetDocumentContentEndpoint(notesContentBucket, noteResource);

    // TODO PUT /note
    // const createNoteFunction = new lambda.Function(this, "CreateNoteFunction", {
    //   vpc: props.vpc,
    //   runtime: lambda.Runtime.PYTHON_3_8,
    //   code: lambda.Code.fromAsset(path.join(__dirname, "../../lambda")),
    //   handler: "mynotes.port.note.handler_create_note",
    //   memorySize: 256,
    //   environment: {
    //     "NOTES_CONTENT_BUCKET_NAME": notesContentBucket.bucketName,
    //     "NOTES_TABLE_NAME": notesTable.tableName
    //   }
    // });

    const lambdaEnvironment = {
      "NOTES_CONTENT_BUCKET_NAME": notesContentBucket.bucketName,
      "NOTES_TABLE_NAME": notesTable.tableName
    }

    const createNoteFunction = new pylambda.PythonFunction(this, "CreateNoteFunction", {
      functionName: "CreateNote",
      description: "Create note",
      vpc: props.vpc,
      entry: "../lambda", // required
      index: "mynotes/port/notes.py",
      handler: "handler_create_note",
      runtime: lambda.Runtime.PYTHON_3_8,
      memorySize: 256,
      environment: lambdaEnvironment
    });

    notesTable.grantFullAccess(createNoteFunction);
    notesContentBucket.grantReadWrite(createNoteFunction);

    noteResource.addMethod("POST", new apigw.LambdaIntegration(createNoteFunction))

    const noteResourceWithId = noteResource.addResource("{id}");
    
    const deleteNoteFunction = new pylambda.PythonFunction(this, "DeleteNoteFunction", {
      functionName: "DeleteNote",
      description: "Delete note",
      vpc: props.vpc,
      entry: "../lambda", // required
      index: "mynotes/port/notes.py",
      handler: "handler_delete_by_id",
      runtime: lambda.Runtime.PYTHON_3_8,
      memorySize: 256,
      environment: lambdaEnvironment
    });

    notesTable.grantFullAccess(deleteNoteFunction);
    notesContentBucket.grantReadWrite(deleteNoteFunction);

    noteResourceWithId.addMethod("DELETE", new apigw.LambdaIntegration(deleteNoteFunction))

    const findNoteByIdFunction = new pylambda.PythonFunction(this, "FindNoteByIdFunction", {
      functionName: "FindNoteById",
      description: "Find note by id",
      vpc: props.vpc,
      entry: "../lambda", // required
      index: "mynotes/port/notes.py",
      handler: "handler_find_by_id",
      runtime: lambda.Runtime.PYTHON_3_8,
      memorySize: 256,
      environment: lambdaEnvironment
    });

    notesTable.grantFullAccess(findNoteByIdFunction);
    notesContentBucket.grantReadWrite(findNoteByIdFunction);

    noteResourceWithId.addMethod("GET", new apigw.LambdaIntegration(findNoteByIdFunction))

    // TODO  DELETE /note/{noteId}

    // TODO PUT /note

    // TODO GET /note
  }

  private setUpGetDocumentContentEndpoint(assetsBucket: s3.Bucket, noteResource: apigw.Resource): void {
    // const assetsBucket = new s3.Bucket(this, "static-assets", {
    //   bucketName: "my-notes-assets"
    // });

    const executeRole = new iam.Role(this, "api-gateway-s3-assumer-role", {
      assumedBy: new iam.ServicePrincipal("apigateway.amazonaws.com"),
      roleName: "API-Gateway-S3-Integration-Role"
    });
    executeRole.addToPolicy(
      new iam.PolicyStatement({
        resources: [assetsBucket.bucketArn],
        actions: ["s3:Get"]
      })
    );
    assetsBucket.grantReadWrite(executeRole);

    const s3Integration = this.createS3Integration(assetsBucket, executeRole);

    this.addAssetsEndpoint(noteResource, s3Integration);
  }

  private createS3Integration(assetsBucket: s3.Bucket, executeRole: iam.Role): apigw.AwsIntegration {
    return new apigw.AwsIntegration({
      service: "s3",
      integrationHttpMethod: "GET",
      path: `${assetsBucket.bucketName}/{folder}/{key}`,
      options: {
        credentialsRole: executeRole,
        integrationResponses: [
          {
            statusCode: "200",
            responseParameters: {
              "method.response.header.Content-Type": "integration.response.header.Content-Type"
            }
          }
        ],
        requestParameters: {
          "integration.request.path.folder": "method.request.path.folder",
          "integration.request.path.key": "method.request.path.key"
        }
      }
    });
  }

  private addAssetsEndpoint(noteResource: apigw.Resource, s3Integration: apigw.AwsIntegration): void {
    noteResource
      .addResource("assets")
      .addResource("{folder}")
      .addResource("{key}")
      .addMethod("GET", s3Integration, {
        methodResponses: [
          {
            statusCode: "200",
            responseParameters: {
              "method.response.header.Content-Type": true
            }
          }
        ],
        requestParameters: {
          "method.request.path.folder": true,
          "method.request.path.key": true,
          "method.request.header.Content-Type": true,
        }
      });
  }
}
