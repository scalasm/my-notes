# Developing with Localstack
We can use Locastack

In your `$HOME/.bashrc` add:
```
alias awslocal="aws --endpoint-url http://0.0.0.0:4566"
```
(restart or open a new terminal!)

## Start
```
(lambda-sXTDgYc4) mario@scalasm-xps:~/src/my-notes/my-notes/lambda$ make -f localstack/Makefile up
```
## Stop
```
(lambda-sXTDgYc4) mario@scalasm-xps:~/src/my-notes/my-notes/lambda$ make -f localstack/Makefile down
```

# Useful CLI snippets for DynamoDB

```
awslocal dynamodb describe-table --table-name Notes

awslocal dynamodb scan --table-name Notes --index-name SearchByAuthorAndTypeIndex
```