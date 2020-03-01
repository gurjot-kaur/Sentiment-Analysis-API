# Case Study 2

## Install instructions

### Create an Amazon Web Services (AWS) account


If you already have an account, skip this step.

Go to this [link](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fportal.aws.amazon.com%2Fbilling%2Fsignup%2Fresume&client_id=signup) and follow the instructions.
You will need a valid debit or credit card. You will not be charged, it is only to validate your ID.


### Install AWS Command Line Interface (AWSCLI)

Install the AWS CLI Version 1 for your operating system. Please follow the appropriate link below based on your operating system.
Linux
macOS
Windows
* Please make sure you add the AWS CLI version 1 executable to your command line Path.
Verify that AWS CLI is installed correctly by running aws --version.

You should see something similar to aws-cli/1.17.0 Python/3.7.4 Darwin/18.7.0 botocore/1.14.0.
Configuring the AWS CLI

You need to retrieve AWS credentials that allow your AWS CLI to access AWS resources.

Sign into the AWS console. This simply requires that you sign in with the email and password you used to create your account. If you already have an AWS account, be sure to log in as the root user.
Choose your account name in the navigation bar at the top right, and then choose My Security Credentials.
Expand the Access keys (access key ID and secret access key) section.
Press Create New Access Key.
Press Download Key File to download a CSV file that contains your new AccessKeyId and SecretKey. Keep this file somewhere where you can find it easily.
Now, you can configure your AWS CLI with the credentials you just created and downloaded.

In your Terminal, run aws configure.

i. Enter your AWS Access Key ID from the file you downloaded.
ii. Enter the AWS Secret Access Key from the file.
iii. For Default region name, enter us-east-1.
iv. For Default output format, enter json.

Run aws s3 ls in your Terminal. If your AWS CLI is configured correctly, you should see nothing (because you do not have any existing AWS S3 buckets) or if you have created AWS S3 buckets before, they will be listed in your Terminal window.

* If you get an error, then please try to configure your AWS CLI again.

### Install Postman

Follow the instructions of your operating system:

[macOS](https://learning.postman.com/docs/postman/launching-postman/installation-and-updates/#installing-postman-on-mac)

[Windows](https://learning.postman.com/docs/postman/launching-postman/installation-and-updates/#installing-postman-on-windows)
