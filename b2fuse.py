#!/usr/bin/env python
# -*- coding: utf-8 -*-

#The MIT License (MIT)

#Copyright (c) 2015 Sondre Engebraaten

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import argparse
import logging
import yaml

from fuse import FUSE

from b2fuse_main import B2Fuse


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("mountpoint", type=str, help="Mountpoint for the B2 bucket")

    parser.add_argument('--enable_hashfiles', dest='enable_hashfiles', action='store_true')
    parser.set_defaults(enable_hashfiles=False)

    parser.add_argument('--use_disk', dest='use_disk', action='store_true')
    parser.set_defaults(use_disk=False)
    
    parser.add_argument('--version',action='version', version="B2Fuse version 1.3")

    parser.add_argument(
        "--account_id",
        type=str,
        default=None,
        help="Account ID for your B2 account (overrides config)"
    )
    parser.add_argument(
        "--application_key",
        type=str,
        default=None,
        help="Application key for your account  (overrides config)"
    )
    parser.add_argument(
        "--bucket_id",
        type=str,
        default=None,
        help="Bucket ID for the bucket to mount (overrides config)"
    )

    parser.add_argument("--temp_folder", type=str, help="Temporary file folder")
    parser.add_argument("--config_filename", type=str, help="Config file")
    
    
    parser.add_argument("-o", type=str, help=argparse.SUPPRESS)

    return parser


def load_config(config_filename):
    with open(config_filename) as f:
        return yaml.load(f.read())

def default_arg(arg, default=None):
    if arg:
        return arg
    else:
        return default
        
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING, format="%(asctime)s:%(levelname)s:%(message)s")

    parser = create_parser()
    args = parser.parse_args()
    
    if args.config_filename:
        config = load_config(args.config_filename)
    else:
        config = {}
        
        
    if args.o:
        print args.o
        
        kvs = dict(map(lambda kv: kv.split("="), args.o.split(",")))
        
        if kvs.get("account_id") is not None:
            config["accountId"] = kvs.get("account_id")
            
        if kvs.get("application_key") is not None:
            config["applicationKey"] = kvs.get("application_key")
                
        if kvs.get("bucket_id") is not None:
            config["bucketId"] = kvs.get("bucket_id")
        
    #Required args
    config["accountId"] = default_arg(args.account_id)
    config["applicationKey"] = default_arg(args.application_key)
    config["bucketId"] = default_arg(args.bucket_id)

    #Optional args
    config["enableHashfiles"] = default_arg(args.enable_hashfiles, False)
    config["tempFolder"] = default_arg(args.temp_folder, ".tmp/")
    config["useDisk"] = default_arg(args.use_disk, False)
    
    #Check required parameters
    assert config.get("accountId"), "Account ID not given"
    assert config.get("applicationKey"), "Application key not given"
    assert config.get("bucketId"), "Bucket ID not given"

    with B2Fuse(
        config["accountId"], config["applicationKey"], config["bucketId"],
        config["enableHashfiles"], config["tempFolder"], config["useDisk"]
    ) as filesystem:
        FUSE(filesystem, args.mountpoint, nothreads=True, foreground=True)
