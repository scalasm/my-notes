// Copyright Mario Scalas 2021. All Rights Reserved.
// This file is licensed under the MIT License.
// License text available at https://opensource.org/licenses/MIT

import * as cdk from "aws-cdk-lib";
import * as cognito from "aws-cdk-lib/aws-cognito";
import * as constructs from "constructs";

/**
 * Configuration properties for Auth resources.
 */
export interface AuthStackProps extends cdk.NestedStackProps {
    /**
     * The user pool name that will be associated to the Cognito User Pool.
     */
    readonly userPoolName: string;
}

/**
 * Auth resources across stacks.
 */
export class AuthStack extends cdk.NestedStack {
    public readonly userPool: cognito.UserPool;
    public readonly userPoolClient: cognito.UserPoolClient;
    public readonly identityPool: cognito.CfnIdentityPool;

    public readonly userPoolIdOutput: cdk.CfnOutput;
    public readonly userPoolClientIdOutput: cdk.CfnOutput;
    public readonly identityPoolIdOutput: cdk.CfnOutput;

    public readonly regionOutput: cdk.CfnOutput;

    constructor(scope: constructs.Construct, id: string, props: AuthStackProps) {
        super(scope, id, props);

        this.userPool = new cognito.UserPool(this, "user-pool", {
            userPoolName: props.userPoolName,
            selfSignUpEnabled: true, // Allow users to sign up
            autoVerify: { email: true }, // Verify email addresses by sending a verification code
            signInAliases: { email: true } // Set email as alias
        });

        this.userPoolClient = new cognito.UserPoolClient(this, "user-pool-client", {
            userPool: this.userPool,
            authFlows: {
                adminUserPassword: true,
                userSrp: true
            },
            generateSecret: false // No need to generate a secret for webapps running in browser
        });

        this.identityPool = new cognito.CfnIdentityPool(this, "identity-pool", {
            allowUnauthenticatedIdentities: true,
            cognitoIdentityProviders: [{
                clientId: this.userPoolClient.userPoolClientId,
                providerName: this.userPool.userPoolProviderName
            }]
        });

        this.identityPoolIdOutput = new cdk.CfnOutput(this, "IdentityPoolId", {
            exportName: "IdentityPoolId",
            value: this.identityPool.ref || ""
        });
        this.userPoolClientIdOutput = new cdk.CfnOutput(this, "UserPoolClientId", {
            exportName: "UserPoolClientId",
            value: this.userPoolClient.userPoolClientId || ""
        });
        this.userPoolIdOutput = new cdk.CfnOutput(this, "UserPoolId", {
            exportName: "UserPoolId",
            value: this.userPool.userPoolId || ""
        });
        this.regionOutput = new cdk.CfnOutput(this, "Region", {
            value: this.region || ""
        });
    }
}