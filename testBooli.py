import time
import requests
from hashlib import sha1
import random
import string
import json


"""
Make a sample call to the Booli API asking for all listings in 'Nacka' in JSON format, 
using 'YOUR_CALLER_ID' and 'YOUR_PRIVATE_KEY' for authentication
"""

callerId = ""

timestamp = str(int(time.time()))
unique = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
hashstr = sha1((callerId + timestamp + "YOUR_PRIVATE_KEY" + unique).encode('utf-8')).hexdigest()

headers = {'Accept': 'application/vnd.booli-v2+json'}
url = "http://api.booli.se/listings?q=nacka&callerId=" + callerId + "&time=" + timestamp + "&unique=" + unique + "&hash=" + hashstr
response = requests.get(url, headers=headers)

if(response.status_code != 200):
    print("fail")
print(response)
# result = json.loads(response.text)