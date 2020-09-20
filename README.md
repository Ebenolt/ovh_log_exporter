# OVH PCC Log Exporter + Mailer
Automatically export ovh pcc logs to csv and mail it

## Requirements
 
 * python3 and pip (python3-pip)
 * pip: requests, ovh (pip install requests ovh)
 * OVH Account with API access
 * SMTP user + server

## How to config

Create a token here: https://eu.api.ovh.com/createToken
Once configured and created token, add `application_key` and `application_secret` into `config.ini`

You can now run `python3 get_consumer.py` it will check your IDs and ask for a consumer key.
Once you got it, go to the link specified to enable it and copy it into `config.ini` at OVH:`consumer_key`

You can now finalize configuration in `config.ini` with pcc name, mail credentials and servers, and mail receivers.

You can check if config is valid by running `python3 testconf.py`

## How to use

Simply run `python3 ovh_log_exporter.py` on the 1st time it will take long, and then it will automatically take the D-1 data through last day file to reduce API request / processing time
It will log everything to console and to 'log/Logs_OVH_DD_MM_YYYY.log' and then send it by mail to config.ini:receivers


