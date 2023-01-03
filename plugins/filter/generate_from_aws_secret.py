# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import boto3
import json
import os
import re
import base64

DOCUMENTATION = """
    lookup: generate_from_aws_secret
    author: Zdravko Posloncec <zdravko@modul8.dev>
    version_added: '1.1.7'
    short_description: generate config_map and/or secret variables from AWS Secret
    description:
        - This filter parses the variables from AWS Secret and map the values pointed to different vault key's with original values
        - used within templating engine for k8s config_map and secrets
    options:
      type:
        description: 
          - config or secret
        required: True
    notes:
      - https://github.com/modul8dev/ansible-plugins
    
    example:
      - "{{ my_service.config_map | modul8dev.plugins.generate_from_aws_secret('config') | to_nice_yaml }}"
      - "{{ my_service.secret | modul8dev.plugins.generate_from_aws_secret('secret') | to_nice_yaml }}"
"""


def pull_secret(path, key):
    aws_region = os.getenv('AWS_REGION')
    client = boto3.client('secretsmanager', region_name=aws_region)
    response = client.get_secret_value(SecretId=path)
    secret = json.loads(response['SecretString'])
    return secret[key]


def encode(secret):
    message_bytes = secret.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


class FilterModule(object):
    def filters(self):
        return {'generate_from_aws_secret': self.generate_from_aws_secret}
        

    def generate_from_aws_secret(self, vars, type):   
        dict = {}
        regex = r"secret_path:.[a-zA-Z0-9_\/ ]*"
        
        for k, v in vars.items():
            match = re.findall(regex, v)
            if match:
                for m in match:
                    var = re.split(":| ", m)
                    s = pull_secret(var[1], var[2])
                    v = re.sub(regex, s, v, 1)
                if type.__eq__("secret"):
                    v = encode(v)
                dict[k] = v
            else:
                if type.__eq__("secret"):
                    v = encode(v)
                dict[k] = v
        return dict
