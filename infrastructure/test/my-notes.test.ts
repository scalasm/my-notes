import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as MyNotes from '../lib/my-notes-application-stack';

// example test. To run these tests, uncomment this file along with the
// example resource in lib/my-notes-stack.ts
test('SQS Queue Created', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new MyNotes.MyNotesApplicationStack(app, 'MyTestStack');
    // THEN
    const template = Template.fromStack(stack);

    template.hasResourceProperties('AWS::Cognito::UserPool', {
        userPoolName: "MyNotes User Pool"
    });
});
