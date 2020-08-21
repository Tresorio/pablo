#!/usr/bin/env python3.6
import os
import sys
from hashlib import md5
from argparse import ArgumentParser

parser = ArgumentParser(description='Compare an S3 etag to a local file')
parser.add_argument('inputfile', help='The local file')
parser.add_argument('etag', help='The etag from s3')
args = parser.parse_args()

def factor_of_1MB(filesize, num_parts):
    x = filesize / int(num_parts)
    y = x % 1048576
    return int(x + 1048576 - y)

def calc_etag(inputfile, partsize):
    md5_digests = []
    with open(inputfile, 'rb') as f:
        for chunk in iter(lambda: f.read(partsize), b''):
            md5_digests.append(md5(chunk).digest())
    return md5(b''.join(md5_digests)).hexdigest() + '-' + str(len(md5_digests))

def possible_partsizes(filesize, num_parts):
    return lambda partsize: partsize < filesize and (float(filesize) / float(partsize)) <= num_parts

def main():
    filesize  = os.path.getsize(args.inputfile)
    num_parts = int(args.etag.split('-')[1])

    partsizes = [ ## Default Partsizes Map
        8388608, # aws_cli/boto3
        15728640, # s3cmd
        factor_of_1MB(filesize, num_parts) # Used by many clients to upload large files
    ]

    for partsize in filter(possible_partsizes(filesize, num_parts), partsizes):
        if args.etag == calc_etag(args.inputfile, partsize):
            print('Local file matches')
            sys.exit(0)

    print('Couldn\'t validate etag')
    sys.exit(1)

if __name__ == "__main__":
    main()