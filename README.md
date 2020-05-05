# cf-spring-boot-test

This repository provision a spring boot application in a scalable and fault-tolerant way in the AWS cloud. See the instructions below for how to deploy and run this application.


# Dependencies
* `Python`: > 3
* `An AWS account of course`
* `A bucket in S3 and eu-west-1 region`
* `Import a valid key to access via ssh in the bastion host`


# Limitations
Currently multi region is not taken into account and the region where it is deployed is in EU-WEST-1

All instances used are of type t2.micro and no other instance type can be chosen. Also, availability zones, are hardcoded

# Components

In the current infrastructure we have:

* Bastion host

* Nat instances

* RDS

* ASG

* EC2

* ELB

* Cloudwatch

* VPC, Subnets, Route tables, SG

# Deploy application

### Run cfprovision

1. Provision infrastructure: 

Please config your aws api access in your credentials file 
```
pip install -r requeriments.txt
cd cfprovision
python3 cfprovision.py --file config.yaml
``` 
This command will provision infrastructure and deploy application from a config file. 

The output while is executing:
````
Creating api-users
...waiting for stack to be ready...
````


The application takes into account when it is a new deployment of the stack or it has to be updated



2. Config file: 

By default, the file config.yaml exists and we indicate it as a parameter. This configuration file has the following fields:

* key_name: SSH key name
* s3_template_bucket_name: s3 bucket name where reside stack templates (template/infra)

* db_username: username to access database. Used in RDS and Spring boot application

* db_password: password to access database. Same db_username

* environment: Environment name to deploy a stack. Multiples environments in the same account

* stack_name: Stack name, by default api-users

* version: Application version. Only change when you want update application

* region: Ireland region, currently

# TEST

To execute unit test for cfprovision
````
python3 -m unittest test/cfprovisiontest.py
````

# To improve

* Use route53 to access rds
* Use parameter store to save config
* ALB as load balancer 


# Questions
For any questions you can create an issue in that repository
