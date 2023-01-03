# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import hvac
import json
import os


DOCUMENTATION = """
  lookup: vault_version
  author: Zdravko Posloncec
  version_added: "1.1.6" 
  short_description: read vault path and return version metadata
  description:
      - This lookup returns the metadata for a defined path in json format
  options:
    _paths:
      description: path(s) of vault folders to read
      required: True
    mount_point:
      description:
            - Start point for the secret path
      type: string
      required: True
  notes:
    - https://github.com/X-Margin-Inc/ansible-plugins

  example:
    - "{{ lookup('xmargin_devops.plugins.get_vault_version', 'my_secret/path/', mount_point='test', wantlist=True) }}"

"""

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase

class LookupModule(LookupBase):

    def run(self, paths, mount_point, variables=None, **kwargs):

      versions = {}

      ret = paths
      for path in paths:
        vault_url = os.getenv('VAULT_ADDR')
        client = hvac.Client(url=vault_url, namespace='admin')
        list_response = client.secrets.kv.v2.list_secrets(
            path=path,
            mount_point=mount_point
        )
        folders = list_response['data']['keys']

        for folder in folders:
            secret_version_response = client.secrets.kv.v2.read_secret_version(
               path=path + '/' + folder,
               mount_point=mount_point
            )
            versions[folder] = secret_version_response['data']['metadata']['version']
        
        json_data = json.dumps(versions)

      return json_data
