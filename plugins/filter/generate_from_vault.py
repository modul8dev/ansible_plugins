# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import boto3
import json
import hvac
import os
import re
import base64

DOCUMENTATION = """
    lookup: generate_from_vault
    author: Zdravko Posloncec <z.posloncec@gmail.com>
    version_added: '1.1.7'
    short_description: generate config_map and/or secret variables from HashiCorp Vault/AWS Secret Manager
    description:
        - This filter parses the variables from Hashicorp Vault and map the values pointed to different vault key's with original values
        - used within templating engine for k8s config_map and secrets
    options:
      type:
        description: 
          - config or secret
        required: True
    notes:
      - https://github.com/X-Margin-Inc/ansible-plugins
    
    example:
      - "{{ my_service.config_map | xmargin_devops.plugins.generate_from_vault('config') | to_nice_yaml }}"
      - "{{ my_service.secret | xmargin_devops.plugins.generate_from_vault('secret') | to_nice_yaml }}"
"""


def pull_vault_secret(path, key, namespace='admin'):
    vault_url = os.getenv('VAULT_ADDR')
    client = hvac.Client(url=vault_url, namespace=namespace)
    secret = client.read(path)['data']
    return secret['data'][f'{key}']


def pull_asm_secret(path, key):
    aws_region = os.getenv('AWS_REGION', "eu-central-1")
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
        return {'generate_from_vault': self.generate_from_vault}
        

    def generate_from_vault(self, vars, type):
        result = {}
        vault_regex = r"vault_path:.[a-zA-Z0-9_\/ ]*"
        asm_regex = r"asm_path:.[a-zA-Z0-9_\/ ]*"
    
        for k, v in vars.items():   
            vault_match = re.findall(vault_regex, v)
            asm_match = re.findall(asm_regex, v)
                  
            if not vault_match and not asm_match:
                if type == "secret":
                    v = encode(v)
                result[k] = v
            else:
                for m in vault_match:
                    var = re.split(":| ", m)
                    s = pull_vault_secret(var[1], var[2])
                    v = re.sub(vault_regex, s, v, 1)
                for m in asm_match:
                    var = re.split(":| ", m)
                    s = pull_asm_secret(var[1], var[2])
                    v = re.sub(asm_regex, s, v, 1)
                if type == "secret":
                    v = encode(v)
                result[k] = v
                
        return result
