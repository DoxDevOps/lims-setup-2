#!/bin/bash

echo letmein| sudo -S tar -xvf /var/www/html/iBLIS.tar.gz

sudo mv /var/www/html/var/lib/jenkins/workspace/lims-setup_master/iBLIS /var/www/html/iBLIS

sudo chmod -R 777 /var/www/html/iBLIS
