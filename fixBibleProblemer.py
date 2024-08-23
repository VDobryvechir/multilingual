from common import *

readyList = ["MAT","MRK","LUK","JHN"]


# ------------------------------------------------------------------------------------------------------ 

NulList=""
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
                 problemData += '<a  target="_blank" href="https://www.bible.com/bible/'+urlHer+'">' + code + " " + strChapter + "</a> " + str(verses) + " en " + str(current) + " "+ lang + " <span><form target='_blank' action='https://localhost:7001/api/fixverse' method='GET' accept-charset='utf-8'><button type='submit'>empty at</button><input type='text' name='line' style='width:50px'/><input type='hidden' name='id' value='"+lang+code+strChapter+"' /><input type='hidden' name='content' value='0' /><input type='hidden' name='total' value='" + str(current) + "'></form></span> <span><form  target='_blank' action='https://localhost:7001/api/fixverse' method='GET'  accept-charset='utf-8'><button type='submit'>break at</button><input type='text' name='content' style='width:300px' /><input type='hidden' name='id' value='"+lang+code+strChapter+"' /><input type='hidden' name='line' value='0'/><input type='hidden' name='total' value='" + str(current) + "'></form></span><br/>\n"
                 problemCount+=1
            index+=1
    if problemCount==0:
        NulList += " " + code
    else:
        fileName = "../problemer/"+code+".html"
        problemData = str(problemCount) + " problemer<br/>\n" + problemData
        with open(fileName, "w", encoding='utf-8') as fwrt:
               fwrt.write(problemData)
        print(str(problemCount) + " in " + code)
if NulList!="":
    print("no problem in "+NulList)





