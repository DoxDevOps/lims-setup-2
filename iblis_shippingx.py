import requests
import json
import platform
import subprocess
import os
import tarfile
from fabric import Connection
from dotenv import load_dotenv
load_dotenv()

def get_xi_data(url):
    response = requests.get(url)
    data = json.loads(response.text)
    data = data[0]['fields']
    return data


""" 
* sends SMS alerts
* @params url, params
* return dict
"""


def alert(url, params):
    headers = {'Content-type': 'application/json; charset=utf-8'}
    r = requests.post(url, json=params, headers=headers)
    return r


recipients = ["+2659980062371", "+2659982767121","+2659953166331","+2659914563411","+2659993422301","+2659952461441"]

cluster = get_xi_data('http://10.44.0.52/sites/api/v1/get_single_cluster/30')

for site_id in cluster['site']:
    site = get_xi_data('http://10.44.0.52/sites/api/v1/get_single_site/' + str(site_id))

    # functionality for ping re-tries
    count = 0

    while (count < 3):

        # lets check if the site is available
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        if subprocess.call(['ping', param, '1', site['ip_address']]) == 0:
            
            # ship iBLIS to remote site
            push_iblis = "rsync " + "-r $WORKSPACE/iBLIS "+ site['username'] + "@" + site[
                'ip_address'] + ":/var/www/html/"
            os.system(push_iblis)
                
             # ship nlims_controller
            push_controller = "rsync " + "-r $WORKSPACE/nlims_controller "+ site['username'] + "@" + site[
                'ip_address'] + ":/var/www/"
            os.system(push_controller)
         
             # ship syncroniser
            push_syncroniser = "rsync " + "-r $WORKSPACE/nlims_data_syncroniser "+ site['username'] + "@" + site[
                'ip_address'] + ":/var/www/"
            os.system(push_syncroniser)
            
              # ship Genexpert driver
            push_genexpert = "rsync " + "-r $WORKSPACE/GeneXpert_Machine_Driver "+ site['username'] + "@" + site[
                'ip_address'] + ":/var/www/"
            os.system(push_genexpert)
                
              # ship websocket
            push_websocket = "rsync " + "-r $WORKSPACE/lims-websocket "+ site['username'] + "@" + site[
                'ip_address'] + ":/var/www/"
            os.system(push_websocket)
            
            # send sms alert
            for recipient in recipients:
                msg = "Hi there,\n\nDeployment of iBlis to " + site['name'] + " completed succesfully.\n\nThanks!\nEGPAF HIS."
                params = {
                    "api_key": os.getenv('API_KEY'),
                    "recipient": recipient,
                    "message": msg
                }
                alert("http://sms-api.hismalawi.org/v1/sms/send", params)

            count = 3
        else:
            count = count + 1

            # make sure we are sending the alert at the last pint attempt
            if count == 3:
                for recipient in recipients:
                    msg = "Hi there,\n\nDeployment of iBlis for " + site['name'] + " failed to complete after several connection attempts.\n\nThanks!\nEGPAF HIS."
                    params = {
                        "api_key": os.getenv('API_KEY'),
                        "recipient": recipient,
                        "message": msg
                    }
                    alert("http://sms-api.hismalawi.org/v1/sms/send", params)
