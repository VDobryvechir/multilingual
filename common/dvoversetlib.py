from urllib.request import Request, urlopen
import json
                      
def helpTranslate(projId, token, q, srcLang, dstLang, res):
    if srcLang=="nb" or srcLang=="nn":
        srcLang="no"
    if dstLang=="nb" or dstLang=="nn":
        dstLang="no"
    body1 = '{"q":['
    body2 = '],"source":"' + srcLang + '","target":"' + dstLang + '","format":"text"}'
    separ = ''
    for qitem in q:
        body1 += separ + '"' + qitem + '"'
        separ = ','
    n = len(body1)    
    body = (body1 + body2).encode("utf-8")
    req = Request('https://translation.googleapis.com/language/translate/v2', data=body, method="POST")
    req.add_header('Authorization', 'Bearer '+token)
    req.add_header('x-goog-user-project', projId)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    print(f" token=[{token}]  project=[{projId}]")
    content = urlopen(req).read().decode('utf-8')
    data = json.loads(content)
    if ('data' in data) and ("translations" in data['data']):
        items = data["data"]["translations"]
    else:
        print("no data in response: " + content)
        return 0
    for item in items:
        res.append(item["translatedText"])   
    return (len(items), n)

def bulkTranslate(projId, token, qlist, srcLang, dstLang, batchSize, limitation, saver):
    n = len(qlist)
    if n>limitation:
        n=limitation
    i=0
    count = 0
    while i<n:
        res=[]
        amnt = n-i
        if amnt>batchSize:
           amnt=batchSize
        q = qlist[i : i + amnt]
        p, cnt = helpTranslate(projId, token, q, srcLang, dstLang, res)
        count += cnt
        print(str(p) + " translated")    
        if p==amnt:
            i+=amnt
            saver(qlist, res)
        else:
           print('Aborted bulk because returned '+str(p) + ' instead of '+str(amnt))
           break
    return str(i)+" of "+str(n) + " translated " + str(count) + " characters"

def findNonTranslatedEntries(translMap, lang):
    res = []
    for key in translMap:
        entry = translMap[key]
        if entry is not None and "tr" in entry and "or" in entry and len(entry["or"])>0:
            tr = entry["tr"]
            if lang not in tr or tr[lang] is None or len(tr[lang])==0:
                res.append(entry["or"])
    return res
            
def manageBulkTranslate(srcLang, dstLang, batchSize, limitation, config, fileName):
    token = config["sources"]["token"]
    projId = config["sources"]["prosjekt"]
    fileName = fileName.replace("[lang]", srcLang)
    with open(fileName, encoding='utf-8') as fsrc:
        dictMap = json.load(fsrc)
    newList= findNonTranslatedEntries(dictMap, dstLang)
    n=len(newList)
    print(str(n) + " translating " + srcLang + " into " + dstLang + " with " + str(batchSize)+ " batch, " + str(limitation) + " limitation")

    def saverTranslation(src, dst):
        n = len(src)
        for i in range(0, n-1):
            s = src[i].lower()
            d = dst[i]
            dictMap[s]["tr"][dstLang] = d
            with open(fileName, 'w', encoding='utf8') as json_file:
               json.dump(dictMap, json_file, ensure_ascii=False, indent=2)

    res=bulkTranslate(projId, token, newList, srcLang, dstLang, batchSize, limitation, saverTranslation)
    return res

    