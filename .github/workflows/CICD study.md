Youtube Link: https://www.youtube.com/watch?v=ekNhTHtIT1k

`lambda_deployment.yaml`
```yaml
name: Deploy Lambda Function

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2
      - name: Install zip tool
        uses: montudor/action-zip@v1
      - name: Create Zip file for Lambda function
        run: zip -r code.zip .
      - name: AWS CLI v2
        uses: imehedi/actions-awscli-v2@latest
        with:
          args: "lambda update-function-code \
            --function-name arn:aws:<provide your function ARN Here> \
            --zip-file fileb://code.zip"
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: "us-east-1"

```