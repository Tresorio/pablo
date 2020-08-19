import os
import sys
import boto3
from botocore.config import Config

config = Config(
    s3={
      "addressing_style":"virtual"
    },
    signature_version='s3v4',
)

s3_resource = boto3.resource(
    's3',
    aws_access_key_id="test10",
    aws_secret_access_key="test10-secret",
    endpoint_url="https://storage.tresorio.com:9000",
    config=config,
)

def callback(bytes):
    print(bytes)

def downloadDirectory(bucketName, remoteDir, targetDir):
    bucket = s3_resource.Bucket(name=bucketName)
    for object in bucket.objects.filter(Prefix = remoteDir):
        print("Downloading "+object.key+" (size: "+str(object.size)+")...")
        filename=os.path.join(targetDir, object.key)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb+') as file:
            bucket.download_fileobj(object.key, file, Callback=callback)

downloadDirectory("test-bucket2", "ckdfyih8l00003xoxssh1uger", "/tmp")

def uploadDirectory(bucketName, targetDir, remoteDir):
    bucket = s3_resource.Bucket(name=bucketName)
