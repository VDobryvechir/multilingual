from common import *

# ,"ROM","GAL"
readyList = ["MAT","MRK","LUK","JHN","ACT"]


# ------------------------------------------------------------------------------------------------------ 
problem_folder = "../problemer/"
NulList=""
common.dvlib.cleanWholeFolder(problem_folder, "", ".html")
verseSearch=config["sources"]["verseSearch"]

def convertToIntGracefully(s):
    try:
        n = int(s)
    except ValueError:
        return -1
    return n

def parsePageRange(s):
    s = s.strip()
    if len(s)==0 or not (ord(s[0])>=49 and ord(s[0])<=57):
        return -1,-1
    pos = s.find("-")
    if pos<0:
        n = convertToIntGracefully(s)
        return n, -1
    a = convertToIntGracefully(s[0:pos])
    b = convertToIntGracefully(s[pos+1:])
    return a,b

def autoDetectProblems(file_name):
    prb = []
    det = ""
    missed = []
    with open(file_name, encoding='utf-8') as detFile:
        d = detFile.read()
    n = len(d)
    i = 0
    dd = d
    while True:
        pos = dd.find(verseSearch)
        if pos<0:
            break;   
        dd = dd[pos+len(verseSearch):]
        pos = dd.find("<")
        if pos<0:
            break;
        s = dd[:pos]
        a, b = parsePageRange(s)
        if a<=0:
            continue
        print(s, a, b)
        if b>a:
           det+= f"  {a}-{b} " 
    print(file_name)
    return prb, det


for srcItem in catalog:
    if srcItem['resource']!="bible":
        continue
    code = srcItem['code']
    if code not in readyList:
        continue
    chapterAmount = srcItem['chapters'] 
    problemData = '';
    problemCount = 0;
    buildChapter = textOut + "/" + code
    for chapter in range(1, chapterAmount+1):
        strChapter = str(chapter)
        if chapter!=1:
            continue
        chapterDestiny = buildChapter + "/" + strChapter + ".json"
        with open(chapterDestiny, encoding='utf-8') as fchaptSrc:
            chaptSrc = json.load(fchaptSrc)
        targetLanguages = chaptSrc['targetLanguages']
        targetLines = chaptSrc['targetLines']
        verses = len(targetLines[0])
        index = 0
        for lang in targetLanguages:
            current = len(targetLines[index])
            if current!=verses:
                 urlHer = versions['en']['version'] + "/" + code + "." + strChapter + "." + versions['en']['name'] + "?parallel=" + versions[lang]['version']
                 detectedProblems, details = autoDetectProblems(config["sources"]["dataOut"]+"/"+lang+"/"+code+"/"+strChapter+".html")
                 if len(details)>0:
                     problemData += "<div class='details'>" + details+"</div>"    
                 problemData += '<a  target="_blank" href="https://www.bible.com/bible/'+urlHer+'">' + code + " " + strChapter + "</a> " + str(verses) + " en " + str(current) + " "+ lang + "<div style='display:flex'>"
                 indice = 0
                 indMax = len(detectedProblems)
                 while current<verses:
                     empVal = "" if (indice>=indMax) or ("e" not in detectedProblems[indice]) else detectedProblems[indice]["e"]
                     brkVal = "" if (indice>=indMax) or ("b" not in detectedProblems[indice]) else detectedProblems[indice]["b"]
                     problemData += " <div><span><form target='_blank' action='https://localhost:7001/api/fixverse' method='GET' accept-charset='utf-8'><button type='submit'>empty at</button><input type='text' name='line' style='width:50px' value='"+ empVal + "' /><input type='hidden' name='id' value='"+lang+code+strChapter+"' /><input type='hidden' name='content' value='0' /><input type='hidden' name='total' value='" + str(current) + "'></form></span>"
                     problemData += " <span><form  target='_blank' action='https://localhost:7001/api/fixverse' method='GET'  accept-charset='utf-8'><button type='submit'>break at</button><input type='text' name='content' style='width:300px' value='"+ brkVal + "' /><input type='hidden' name='id' value='"+lang+code+strChapter+"' /><input type='hidden' name='line' value='0'/><input type='hidden' name='total' value='" + str(current) + "'></form></span></div>\n"
                     current += 1
                     indice += 1
                 problemData += "</div>" 
                 problemCount+=1
            index+=1
    if problemCount==0:
        NulList += " " + code
    else:
        fileName = problem_folder +code+".html"
        problemData = str(problemCount) + " problemer<br/>\n" + problemData +"""
             <style>.details{padding:7px;color:green;background-color:yellow}</style>
        """    
        with open(fileName, "w", encoding='utf-8') as fwrt:
               fwrt.write(problemData)
        print(str(problemCount) + " in " + code)
if NulList!="":
    print("no problem in "+NulList)





