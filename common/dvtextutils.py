

def addNonRepeatedMapField(dst,field,blocks,separ):
    if blocks is not None and len(blocks)>0:
        if field not in dst or len(dst[field])==0:
            dst[field] = separ.join(blocks)
            return
        s = dst[field]
        items = s.split(separ)
        res=[]
        check = {}
        for item in items:
           t = item.strip()
           if len(t)>0 and t not in check: 
              res.append(t)
              check[t]=1
        for block in blocks:
           t = block.strip();
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
           if key not in m or m[key] is None or len(m[key])==0:
               m[key]=blockMap[key]
           else:
               t = blockMap[key].split(separ)
               addNonRepeatedMapField(m, key, t, separ)
                    