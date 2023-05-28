#!/usr/bin/env python3
import requests
import sys


server = 'http://localhost:3000'

r = requests.get(server)

status = r.raw.status

if status != 200:
    print(f'UNHEALTHY: STATUS {status}')
    sys.exit(1)
else:
    sys.exit(0)