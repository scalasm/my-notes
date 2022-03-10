# My Notes

This is a the business logic for My Notes. 

It is implemented in Python and it uses standard libraries to use AWS Lambda.

# Key-points

* Python 3.8 + typing hints
* [PynamoDB](https://pynamodb.readthedocs.io/) - ORM for AWS DynamoDB
* [Moto](http://docs.getmoto.org/) - Mocking AWS services

# Source organization

* `mynotes` - main package for the Python code (note: we don't use `src/` folder because of the way we AWS CDK packages the lambda function docker image)
* `tests` - unit tests

# Build 

You don't need to build this Python project - you can run tests and develop code, of course. 

Build is performed (at this time) as part of stack resources deployment, see [the parent README.md](../README.md).
