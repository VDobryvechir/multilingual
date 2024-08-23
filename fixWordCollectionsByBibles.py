import urllib.request, json, os, dvlib

f = open('config.json')
config = json.load(f)
f.close()

catIn = config['sources']['catalogIn']
textOut = config['sources']['textOut']
versions = config['versions']
langs = config["languages"]
dicts = {}
for lang in langs:
    dicts[lang] = []
with open(catIn, encoding='utf-8') as fsrc:
    src = json.load(fsrc)

for srcItem in src:
    if srcItem['resource']!="bible":
        continue
    code = srcItem['code']
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
        index = 0
        for lang in targetLanguages:
            dvlib.extractWordsFromLines(dicts[lang],targetLines[index])
            index+=1

for lang in langs:
    ordlist = list(dict.fromkeys(dicts[lang]))
    ordlist.sort()
    print(lang + " " + " all " + str(len(dicts[lang]))+" unique " + str(len(ordlist))) 
    with open('./dict/'+lang+'.json', 'w', encoding='utf8') as json_file:
        json.dump(ordlist, json_file, ensure_ascii=False, indent=2)





