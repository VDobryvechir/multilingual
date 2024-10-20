from urllib.request import Request, urlopen
import json,os, urllib.parse

def convertIntToUtf8(n):
    buf = [n]
    if n>0x7f:
       if n>0x7ff:
           if n>0xffff:
               buf[0] = 0xf0 | ((n>>18) & 7)
               buf.append(0x80 | ((n>>12) & 0x3f))
               buf.append(0x80 | ((n>>6) & 0x3f))
               buf.append(0x80 | ( n & 0x3f))
           else:
               buf[0] = 0xe0 | ((n>>12) & 0xf)
               buf.append(0x80 | ((n>>6) & 0x3f))
               buf.append(0x80 | ( n & 0x3f))
       else:
          buf[0] = 0xc0 | ((n>>6) & 0x1f)
          buf.append(0x80 | ( n & 0x3f))
    b = bytearray(buf)
    return b.decode()

def convertCharToUtf8(line):
    n = int(line)
    sn = convertIntToUtf8(n) 
    return sn

def convertToUtf8(line):
    pos = line.find("&#")
    if pos<0:
        return line
    ferdig = line[:pos]
    print("pos1: ferdig=["+ferdig+"] line=["+line+"]")
    while True:
         line = line[pos+2:]
         pos = line.find(";")
         print("3. "+str(pos)+"; "+line)
         if pos<0:
             ferdig += "&#"
         else:
             c = convertCharToUtf8(line[:pos])
             print("2. "+c+";"+ferdig)
             ferdig += c
             line = line[pos+1:]
         pos = line.find("&#")
         if pos<0:
             break
         ferdig += line[:pos]
                  
    return ferdig + line
         
def extractStringsFromContent(content):
    resContent = []
    for i in range(1, 1000):
        posStart = content.find('class="verse v'+str(i)+'"')
        if posStart<0:
            break
        content = content[posStart+17:]
        posEnd = content.find('class="verse v'+str(i+1)+'"')
        if posEnd<0:
            posEnd = len(content)
        currentContent = content[:posEnd]
        content = content[posEnd:]
        posStart = 0
        resLine = ""
        while True:
            posStart = currentContent.find('class="content"')
            if posStart<0:
                break
            posStart = currentContent.find(">", posStart)
            if posStart<0:
                break	     
            posEnd = currentContent.find("<", posStart+1)
            if posEnd<0:
                break
            currentLine = convertToUtf8(currentContent[posStart+1: posEnd].strip())
            if resLine=="":
                resLine = currentLine
            elif currentLine!="":
                resLine = resLine + " " + currentLine	
            currentContent = currentContent[posEnd:]
        resContent.append(resLine)   
    return resContent

def convertToStr(s):
    srchBeg = 'ChapterContent_content__RrUqA">'
    srchEnd = '</span>'
    srchBegLen = len(srchBeg)     
    srchEndLen = len(srchEnd)
    res = ""
    pos = s.find(srchBeg)
    while pos>0:
        s = s[pos+srchBegLen:]
        pos = s.find(srchEnd)
        if pos<0:
            print("strange " + s)
            break
        line = s[:pos]
        res += line
        pos = s.find(srchBeg, pos)
    return res
  
def convertToStringArray(s):
    res = []
    srch = 'span class="ChapterContent_label__R2PLt">'
    nsrch = len(srch)
    n = len(s) 
    pos = s.find(srch)
    while pos>=0 and pos+nsrch<n:
        c=ord(s[pos+nsrch])
        if c>=48 and c<58:
            break
        else:
            pos = s.find(srch, pos+nsrch)
    while pos>=0:
        nextPos = s.find(srch, pos+nsrch)
        while nextPos>=0 and nextPos+nsrch<n:
             c=ord(s[nextPos+nsrch])
             if c>=48 and c<58:
                  break
             else:
                  nextPos = s.find(srch, nextPos+nsrch)
        line = s[pos+30: nextPos] if nextPos>0 else s[pos+nsrch:]
        pure = convertToStr(line).strip()
        if pure!="":
            res.append(pure)  
        pos = nextPos    
    return res

def evaluateLetter(c):
        if c=="«" or c=="¿" or c=="»" or c=="¡" or c=="“" or c=="”" or c=="„" or c=="‹" or c=="›" or c=="…" or c=="╵" or c=="•" or c==" ":
           return -1
        if c=="‘" or c=='-' or c=="'" or c=="–" or c=="―" or c=="’" or c=="‚" or c=="—" or c=="—":
           return 0 
        n=ord(c)
        if (n>=65 and n<91)or(n>=97 and n<123)or(n>=128):
            return 1
        return -1
   
def extractWordsFromLine(res,s):
     isWordStarted = False
     n = len(s)
     i = 0
     startPos = 0
     endPos = 0
     while i<n:
         c = evaluateLetter(s[i])
         if isWordStarted: 
              match c:
                  case 1:
                      endPos = i+1
                  case -1:
                      isWordStarted = False
                      w= s[startPos: endPos]
                      res.append(w)
         else: 
             match c:
                  case 1:
                      startPos = i
                      endPos = i+1
                      isWordStarted = True
         i+=1
     if isWordStarted:
                      w= s[startPos: endPos]
                      res.append(w)
     return res

def extractWordsFromLines(res,lines):
    for line in lines:
         extractWordsFromLine(res,line)
                      
def copyWordShortInfo(words, lang, diction):
    res=""
    for word in words:
        small=word.lower()
        if small not in diction:
            print(small + " not found in dictionary")
            continue
        entry=diction[small]
        if lang not in entry["tr"]:
            continue
        res+= "*"+word+"="+entry["tr"][lang]
    return res

def copyLineShortInfo(line, diction, langs):
    res={}
    words=[]
    extractWordsFromLine(words,line)
    for lang in langs:
        res[lang] = copyWordShortInfo(words, lang, diction)
    return {"tr":res}

def createUnicaseDictionary(lst):
    res = {}
    for item in lst:
       s = item.lower()
       res[s]=item
    return res

def copyLinePoolShortInfo(current, lang, langDict, langs):
    if lang not in langDict:
        return []
    diction = langDict[lang]
    res=[]
    for line in current:
        res.append(copyLineShortInfo(line, diction, langs))
    return res
 
def cleanWholeFolder(path, prefix, suffix):
    joiner = "" if path.endswith("/") or path.endswith("\\") else "/"
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith(prefix) and entry.name.endswith(suffix):
                os.remove(path + joiner + entry.name)

def findMapNewWords(srcMap, dstMap):
    words=[]
    for key in srcMap:
       if key not in dstMap:
          words.append(key) 
    return words

def saveJsonWithBackup(data, fileName):
    backUp= fileName + "backup"
    if os.path.exists(backUp):
       os.remove(backUp)
    if os.path.exists(fileName):
       os.rename(fileName, backUp)
    with open(fileName, 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

def readMapFromFileIfExists(fileName):
    if not os.path.exists(fileName):
       return {}
    with open(fileName, encoding='utf-8') as fMapData:
          mapData = json.load(fMapData)
    return mapData

def reportError(errorFileName, message):
    if not os.path.exists(errorFileName):
       with open(errorFileName, "w") as file:
          file.write(f"{message}\n")
    else:
       with open(errorFileName, "a") as file:
          file.write(f"{message}\n")



