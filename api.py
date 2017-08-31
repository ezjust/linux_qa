import urllib2
import requests
import certifi

response = requests.get("https://10.10.61.20:8006/apprecovery/admin/", verify=False)
print(response.content)
print(response.status_code)