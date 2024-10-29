import json
import urllib.parse
import common.dvlib

def addNonRepeatedMapField(dst,field,blocks,separ):
    if blocks is not None and len(blocks)>0:
        if field not in dst or len(dst[field])==0:
            dst[field] = separ.join(blocks)
            return
        s = dst[field]
        if not isinstance(s, str):
            s = "strange_type_" + type(s).__name__   
        items = s.split(separ)
        res=[]
        check = {}
        for item in items:
           t = item.strip()
           if len(t)>0 and t not in check: 
              res.append(t)
              check[t]=1
        for block in blocks:
           t = block.strip()
           if len(t)>0 and t not in check:
              res.append(t)
              check[t]=1
        dst[field]=separ.join(res)

def containWholeWord(sw, word):
    pos=0
    n=len(sw)
    m=len(word)
    while pos<n:
       npos = sw.find(word, pos)
       if npos<0:
           return False
       if npos+m==n or sw[npos+m]==" ":
           return True
       pos = npos+1  
    return False

def addNonRepeatedNamedMapField(dst,field,blockMap,separ):
    if len(blockMap)>0:
        if field not in dst or len(dst[field])==0:
            dst[field]=blockMap
            return
        m = dst[field]
        for key in blockMap:
           s = blockMap[key] 
           if key not in m or m[key] is None or len(m[key])==0:
               m[key]= s
           else:
               t = s.split(separ)
               addNonRepeatedMapField(m, key, t, separ)
                    
def addDictionaryMapField(dst,field,blockMap,separ):
    if len(blockMap)>0:
        if field not in dst or len(dst[field])==0:
            dst[field]=blockMap
            return
        m = dst[field]
        for key in blockMap:
           s = blockMap[key] 
           if key not in m or m[key] is None or len(m[key])==0:
               m[key]= s
           else:
               m[key]= s

def foundAllEntriesWithPrefixInFile(fileName, resFileName, pref, beforeEntry, afterEntry, isPrefixed):
    with open(fileName, 'r') as file:
        content = file.read()
    n=len(content)
    lenPref = len(pref)
    pos = 0
    res = set()
    while pos<n:
        pos = content.find(pref,pos)
        if pos<0:
            break
        afterPos = pos+lenPref
        while afterPos<n and ((content[afterPos]>='a' and content[afterPos]<='z') or content[afterPos]=="_" or (content[afterPos]>='A' and content[afterPos]<='Z')):
            afterPos += 1
        word = content[pos:afterPos]
        res.add(word)
        pos = afterPos+1
    cnt=len(res)
    text=""
    res = sorted(res)
    for item in res:
        data = item if isPrefixed else item[lenPref:]
        text +=beforeEntry + data + afterEntry
    with open(resFileName, "w") as file:
        file.write(text)
    return (cnt, res)

def getDictionaryLink(word):
    wrd = urllib.parse.quote_plus(word)
    return "<a target='_blank' href='https://ordbokene.no/nob/bm/"+wrd+"'>" + word + "</a>"

def textContainWord(txt, word, wholeWord):
    pos = txt.find(word)
    if pos<0:
        return False
    if not wholeWord:
        return True
    n = len(txt)
    p = len(word)
    while pos>=0 and pos<n:
        if pos+p>=n:
            return True
        c = txt[pos+p]
        if not (c>='a' and c<='z' or c>='A' and c<='Z' or c=='_' or c>='0' and c<='9'):
            return True
        pos = txt.find(word, pos+p)
    return False
    
def searchAllEntriesInDictionary(src, word, onlyOnce, wholeWord):
    res = {}
    for w in src:
        data = src[w]
        t = json.dumps(data, ensure_ascii=False)
        if textContainWord(t, word, wholeWord):
            res[w] = data
            if onlyOnce:
                break
    return res
        
def highlightenWords(txt, word, prefix, suffix):
    pos = 0
    ln = len(word)
    delta = len(prefix) + len(suffix) + ln
    while pos<len(txt):
        pos = txt.find(word, pos)
        if pos<0:
            break
        txt = txt[:pos] + prefix + word + suffix + txt[pos+ln:]
        pos += delta 
    return txt
        
def recordAllEntriesWithSearchResultsInHtml(config, srcFileName, dstFileName, words, options):
    with open(srcFileName, encoding='utf-8') as fSrc:
        src = json.load(fSrc)
    dst = ""
    onlyOnce = False if "OnlyOnce" not in options else options["OnlyOnce"]
    wholeWords = False if "WholeWord" not in options else options["WholeWord"]
    colorify = False if "Colorify" not in options else options["Colorify"]
    for word in words:
        dst += "<h1>" + word + "</h1>\n"
        entries = searchAllEntriesInDictionary(src, word, onlyOnce, wholeWords)
        for entry in entries:
            dst += "<h2>" + getDictionaryLink(entry) + "</h2>\n<div>\n"
            txt = json.dumps(entries[entry], ensure_ascii=False)
            if colorify:
                txt = highlightenWords(txt, word, "<span style='color:red'>","</span>")
            dst += txt
            dst += "\n</div>\n"
    with open(dstFileName, "w", encoding='utf-8') as file:
        file.write(dst)

def excludeWordsByDictionary(words, exceptDictionary, pref, options):
    emptyAccepted = True if "EmptyAccepted" not in options else options["EmptyAccepted"]
    res = []
    lenPref = len(pref)
    for word in words:
       w = word[lenPref:]
       if w not in exceptDictionary:
           res.append(word)
       elif not emptyAccepted and len(exceptDictionary[w])==0:
           res.append(word)    
    return res 

def extractWordsFromEntry(res, entry):
    if entry is None:
        return
    if "description" in entry:
        common.dvlib.extractWordsFromLine(res, entry["description"])
    if "deepDescription" in entry:
        common.dvlib.extractWordsFromLine(res, entry["deepDescription"])
    if "expression" in entry and entry["expression"] is not None:
        mp = entry["expression"]
        for key in mp:
            common.dvlib.extractWordsFromLine(res, key)
            item = mp[key]
            if "description" in item:
                common.dvlib.extractWordsFromLine(res, item["description"])
            if "deepDescription" in item:
                common.dvlib.extractWordsFromLine(res, item["deepDescription"])

def extractWordsFromEntryMap(res, entryMap):
    if entryMap is None:
        return
    for entry in entryMap:
        common.dvlib.extractWordsFromLine(res, entry)
        extractWordsFromEntry(res, entryMap[entry])

def separateWordsInSet(wordSet, origMap):
    newMap = {}
    for word in wordSet:
        lowerWord = word.lower()
        if lowerWord not in origMap:
            if lowerWord not in newMap or word==lowerWord:
                newMap[lowerWord] = word 
    return newMap

def separateWordsInSetWithNativeFilter(wordSet, origMap, enrichEngine):
    newMap = {}
    for word in wordSet:
        lowerWord = word.lower()
        if lowerWord not in origMap and enrichEngine.isWordNative(word):
            if lowerWord not in newMap or word==lowerWord:
                newMap[lowerWord] = word 
    return newMap

def populateOrigMapWithNewMap(origMap, newMap):
    if newMap is None:
        return
    for word in newMap:  
        if word not in origMap:
            origMap[word] = {"tr": {}, "or": newMap[word]}
    sorted_dict = dict(sorted(origMap.items())) 
    return sorted_dict 
      
def containDictionaryWholeLowerWord(dictMap, lowerWord):
    if dictMap is None:
        return False
    for key in dictMap:
        item = dictMap[key].lower()
        if containWholeWord(item, lowerWord):
            return True
    return False


def extractPhrasesFromEntry(res, entry):
    if entry is None:
        return
    if "description" in entry:
        common.dvlib.extractPhrasesFromLine(res, entry["description"], True, common.dvlib.separatorsSemicolumnComma)
    if "deepDescription" in entry:
        common.dvlib.extractPhrasesFromLine(res, entry["deepDescription"], True, common.dvlib.separatorsSemicolumn)
    if "expression" in entry and entry["expression"] is not None:
        mp = entry["expression"]
        for key in mp:
            common.dvlib.extractPhrasesFromLine(res, key, True, common.dvlib.separatorsSemicolumn)
            item = mp[key]
            if "description" in item:
                common.dvlib.extractPhrasesFromLine(res, item["description"], True, common.dvlib.separatorsSemicolumnComma)
            if "deepDescription" in item:
                common.dvlib.extractPhrasesFromLine(res, item["deepDescription"], True, common.dvlib.separatorsSemicolumn)

def extractPhrasesFromEntryMap(res, entryMap):
    if entryMap is None:
        return
    for entry in entryMap:
        extractPhrasesFromEntry(res, entryMap[entry])

def origCopy(entry, txt):
    res = {"orig": txt}
    if "tr" in entry:
        res["tr"] = entry["tr"]
    return res
    
def enrichLineWithTranslation(txt, sdict, fdict):
    lowCase = txt.lower() 
    if lowCase in sdict:
        return origCopy(sdict[lowCase], txt)
    if lowCase in fdict:
        return origCopy(fdict[lowCase], txt)
    return {}

def enrichTextWithTranslation(txt, sdict, fdict, separ):
    pool = []
    common.dvlib.extractPhrasesFromLine(pool, txt, False, separ)
    res = []
    for line in pool:
        data = enrichLineWithTranslation(line, sdict, fdict)
        res.append(data)
    return res

def enrichMultiWithMono(multiEntry, monoEntry, sdict, fdict):
    if "gender" in monoEntry:
        multiEntry["gender"] = monoEntry["gender"]
    if "declination" in monoEntry:
        multiEntry["declination"] = monoEntry["declination"]
    if "description" in monoEntry:
        multiEntry["description"] = enrichTextWithTranslation(monoEntry["description"], sdict, fdict, common.dvlib.separatorsSemicolumnComma)
    if "deepDescription" in monoEntry:
        multiEntry["deepDescription"] = enrichTextWithTranslation(monoEntry["deepDescription"], sdict, fdict, common.dvlib.separatorsSemicolumn)
    if "expression" in monoEntry and monoEntry["expression"] is not None:
        expressionPool = [];
        data = monoEntry["expression"]
        for line in data:
            item = {"orig": line}
            tran = enrichLineWithTranslation(line, sdict, fdict)
            item["tran"] = tran
            elem = data[line]
            if "description" in elem:
                item["description"]=enrichTextWithTranslation(elem["description"], sdict, fdict, common.dvlib.separatorsSemicolumnComma) 
            if "deepDescription" in elem:
                item["deepDescription"]=enrichTextWithTranslation(elem["deepDescription"], sdict, fdict, common.dvlib.separatorsSemicolumn) 
            expressionPool.append(item)    
        multiEntry["expression"] = expressionPool
        

