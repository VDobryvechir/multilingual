import urllib.request, json, os, dvlib

f = open('config.json')
config = json.load(f)
f.close()

catIn = config['sources']['catalogIn']
textOut = config['sources']['textOut']
versions = config['versions']
token = config["sources"]["token"]
projId = config["sources"]["prosjekt"]
srcLang="nb"
dstLang="en"
folder="./dictionay/"
batchSize=50
limitation=1000000
with open(folder+srcLang+".json", encoding='utf-8') as fsrc:
    rawlist = json.load(fsrc)
n=len(rawlist)
qdict = dvlib.createUnicaseDictionary(rawlist)
qlist = list(qdict.values())
nn = len(qlist)
print(str(nn) + " Translating " + srcLang + " into " + dstLang + " with " + str(batchSize)+ " batch, " + str(n) + " size, " + str(limitation) + " limitation")
res=dvlib.bulkTranslate(projId, token, qlist, srcLang, dstLang, batchSize, limitation)
m=len(res)
diction={}
for i in range(m):
    s=qlist[i]
    t=res[i] 
    tr={}
    tr[dstLang]=t  
    entry = {"tr":tr,"or":s}
    diction[s.lower()] = entry

with open(folder+"s_"+srcLang+'.json', 'w', encoding='utf8') as json_file:
        json.dump(diction, json_file, ensure_ascii=False, indent=2)




