# Ansible collection
Collection of cool ansible plugins

## generate-from-vault
Ansible filter plugin for generating env variables from the HashiCorp vault.
This plugin will allow you to link multiple key's between services and use hashicorp vault as a central place for storing all env variables. More details in this article [...]

## generate-from-aws-secret
Ansible filter plugin for generating env variables from the AWS Secret service.
This plugin will allow you to link multiple key's between services and use aws secret as a central place for storing all env variables.


## list-vault-path
Ansible lookup plugin for generating list of folders from specified HashiCorp vault path. Sometime you need to list folder structure within the vault path. 


## get-vault-version 
Ansible filter plugin to generate secret versions based on the source path. If you need to gather versions for all the folders in some vault path and print it as json.
