import urllib.request, json, os, dvlib

f = open('config.json')
config = json.load(f)
f.close()

catIn = config['sources']['catalogIn']
textOut = config['sources']['textOut']
versions = config['versions']
with open(catIn, encoding='utf-8') as fsrc:
    src = json.load(fsrc)
langDict = {}
langs = config['languages']
for lang in langs:
    if lang!='nb':
        continue
    with open('./dictionary/s_'+lang+'.json', encoding='utf-8') as fdiction:
         langDict[lang] = json.load(fdiction)
for srcItem in src:
    if srcItem['resource']!="bible":
        continue
    code = srcItem['code']
    if code!='LUK':
        continue
    chapterAmount = srcItem['chapters'] 
    buildChapter = textOut + "/" + code
    for chapter in range(1, chapterAmount+1):
        strChapter = str(chapter)
        chapterDestiny = buildChapter + "/" + strChapter + ".json"
        with open(chapterDestiny, encoding='utf-8') as fchaptSrc:
            chaptSrc = json.load(fchaptSrc)
        targetLanguages = chaptSrc['targetLanguages']
        targetLines = chaptSrc['targetLines']
        shortLines = []
        index = 0
        for lang in targetLanguages:
            current = targetLines[index]
            shortLines.append(dvlib.copyLinePoolShortInfo(current, lang, langDict, langs))
            index+=1
        chaptSrc['shortLines'] = shortLines
        with open(chapterDestiny, 'w', encoding='utf8') as json_file:
            json.dump(chaptSrc, json_file, ensure_ascii=False, indent=2)
        print('wrote ' + chapterDestiny)    





