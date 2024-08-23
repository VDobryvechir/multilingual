import urllib.request, json, os, common.dvlib

f = open('../config.json')
config = json.load(f)
f.close()

catalogIn = config['sources']['catalogIn']
dataOut = config['sources']['dataOut']
audioPath = config['sources']['audioPath']
textOut = config['sources']['textOut']
versions = config['versions']

with open(catalogIn, encoding='utf-8') as fcatalog:
    catalog = json.load(fcatalog)

print("Init done")

