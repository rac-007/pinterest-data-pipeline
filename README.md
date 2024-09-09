# Pinterest Data Pipeline

This project involves creating a data pipeline similar to Pinterest's, which processes billions of data points daily to enhance user experience. The pipeline leverages various AWS services to collect, store, process, and analyze data efficiently.

## Overview- Pinterest Data

In order to understand the data Pinterest's Engineers are likely to work with, this project has a script user_posting_emulation_to_console.py, which contains three tables with data resembling data received by the Pinterest API when a POST request is made by a user uploading data to Pinterest:

- **pinterest_data** contains data about posts being updated to Pinterest
- **geolocation_data** contains data about the geolocation of each Pinterest post found in pinterest_data
- **user_data** contains data about the user that has uploaded each post found in pinterest_data

When run the provided script and it prints out pin_result, geo_result and user_result. These each represent one entry in their corresponding table. Lets have a look how these results look like:

![alt text](images/image-1.png)

## Table of Contents
<!-- no toc -->
- [Introduction](#introduction)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Pipeline Tools](#pipeline-tools)
- [Pipeline Building](#pipeline-building)

## Introduction

This project aims to build a data pipeline on AWS that mimics Pinterest's data processing capabilities. The pipeline will collect large volumes of data, process it, and provide valuable insights to enhance user engagement. Key AWS services used include Amazon MSK, Amazon S3, AWS Lambda, Amazon Kinesis(stream processing), and for batch processing Databricks, Spark, Amazon Managed Workflows for Apache Airflow (Amazon MWAA).

## Architecture

![alt text](images/image.png)

## Prerequisites

Before you begin, ensure you have the following:

- An AWS account with appropriate permissions.
- AWS CLI installed and configured on your local machine.
- Basic knowledge of AWS services and data processing concepts.
- Knowledge of Apache kafka, AWS MSK, Kinesis
- Install python, boto3, sqlalchemy, pymysql, json  

## Pipeline Tools

- **AWS MSK**
: Amazon Managed Streaming for Apache Kafka (Amazon MSK) plays a crucial role in data pipeline project by providing a fully managed Apache Kafka service. This service is essential for real-time data streaming and integration, which forms the backbone of the pipeline. Amazon MSK is a critical component of data pipeline, providing robust data ingestion, streaming, and integration capabilities.
- **AWS MSK Connect**
: MSK Connect is a feature of Amazon MSK that makes it easy for developers to stream data to and from their Apache Kafka clusters. 
- **Apache Kafka**
: Apache Kafka is an open-source distributed event streaming platform designed to handle real-time data feeds with high throughput, fault tolerance, and scalability.
- **Kafka Rest Proxy**
: Kafka REST Proxy is a RESTful web service interface for interacting with an Apache Kafka cluster. It provides a way to produce and consume messages, manage topics, and inspect Kafka's state over HTTP without needing to use the native Kafka clients directly. This is particularly useful for applications and systems that do not have direct access to Kafka's native APIs, or when you need a simpler, language-agnostic way to interact with Kafka.
- **AWS API Gateway**  : Amazon API Gateway is a fully managed service that makes it easy for developers to create, publish, maintain, monitor, and secure APIs at any scale. APIs act as the "front door" for applications to access data, business logic, or functionality from your backend services. 
- **Databricks**  :Databricks is used to process and transform extensive amounts of data and explore it through Machine Learning models. It allows organizations to quickly achieve the full potential of combining their data, ETL processes, and Machine Learning. 
- 

## Pipeline Building

### Creating an Apache Cluster With AWS MSK
The first step is to create a kafka cluster, here using AWS MSK. In this project, it was provisioned by the AiCore. The documentation includes a good guide for [getting started](https://docs.aws.amazon.com/msk/latest/developerguide/getting-started.html) and you can follow the steps to get a cluster up and running here. 

### Creating a Client Machine for the Cluster
The next step is to create an Apache Client to communicate with AWS MSK Cluster. In this project an EC2 instance is provisioned as a Apache Client. It was also provisioned by the AiCore Team. You can Create an Amazon linux EC2 instance free tier, create key pair type - RSA, private key file format - '.pem' and select the security group associated with the Kafka cluster (AWS MSK).
Next, edit inbound rules to 'All Traffic'.<br>

We also need to create an IAM role for the client machine.

1. Navigate to the AWS IAM dashboard, select 'Roles' from the left-hand menu and then click on 'Create role'.
2. Select 'AWS service' and 'EC2', then click on 'Next'.
3. On the next page, select 'Create policy'.
4. In the policy editor, choose JSON format and paste in the following policy. Note: this policy is somewhat open - a more restrictive policy would be more appropriate for a production environment
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "kafka:ListClustersV2",
                "kafka:ListVpcConnections",
                "kafka:DescribeClusterOperation",
                "kafka:GetCompatibleKafkaVersions",
                "kafka:ListClusters",
                "kafka:ListKafkaVersions",
                "kafka:GetBootstrapBrokers",
                "kafka:ListConfigurations",
                "kafka:DescribeClusterOperationV2"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "kafka-cluster:*",
            "Resource": [
                "arn:aws:kafka:*:<AWS-UUID>:transactional-id/*/*/*",
                "arn:aws:kafka:*:<AWS-UUID>:group/*/*/*",
                "arn:aws:kafka:*:<AWS-UUID>:topic/*/*/*",
                "arn:aws:kafka:*:<AWS-UUID>:cluster/*/*"
            ]
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "kafka:*",
            "Resource": [
                "arn:aws:kafka:*:<AWS-UUID>:cluster/*/*",
                "arn:aws:kafka:*:<AWS-UUID>:configuration/*/*",
                "arn:aws:kafka:*:<AWS-UUID>:vpc-connection/*/*/*"
            ]
        }
    ]
}

```
   
5. On the next page, give the policy a descriptive name and save the policy.
6. Back in the create role tab in the browser, click refresh to show the new policy and select the policy.
7. Click 'Next', give the role a descriptive name and save the role.
8. In the EC2 dashboard, click on the client instance.
9. Under 'Actions' and 'Security', click on 'Modify IAM role'.
10.  Select the role just created and click on 'Update IAM role'.

### Install Kafka on the client machine
1. Once the new instance is up and running, connect via SSH to interact with the instance using the command line. 
2. Follow the instructions in the 'SSH' tab to connect to the instance.
   
```
# make sure key is not publicly viewable
chmod 400 pinterest-kafka-client-keypair.pem
# connect
ssh -i "pinterest-kafka-client-keypair.pem" ec2-user@<instance-public-DNS>
```
3. Once you get connected to EC2, run the following commands:
```
# install Java - required for Kafka to run
sudo yum install java-1.8.0
# download Kafka - must be same version as MSK cluster created earlier
wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
# unpack .tgz
tar -xzf kafka_2.12-2.8.1.tgz
```   
