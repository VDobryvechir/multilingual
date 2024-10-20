from common import *
import common.dvtextutils, common.dvlib
from common.enrich_mono_dictionary import EnrichMonoDictionary

langFilter = ["nb"]
# 2 test for small data and not affecting origin
# 1 test for all data but not affecting origin
# 0 real production engine
testMode = (0, "[folder]multi_[lang].json","[folder]mono_[lang].json")

#--------------------------------------------------------------------------------------------------------
langs = config["languages"]
for lang in langs:
    if lang not in langFilter:
        continue
    stage = 0
    enrichEngine = EnrichMonoDictionary(lang, config)
    folder = config["sources"]["testFolder"]
    dst = config["sources"]["multiDictionary"].replace("[lang]",lang)
    src = config["sources"]["monoDictionary"].replace("[lang]",lang) 
    match testMode[0]:
       case 2:
          dst = testMode[1].replace("[lang]",lang).replace("[folder]",folder)
          src = testMode[2].replace("[lang]",lang).replace("[folder]",folder)
       case 1:
          stage = 1
       case 0:
          stage = 2
    with open(src, encoding='utf-8') as fsrc:
       srcMap = json.load(fsrc)
    with open(dst, encoding='utf-8') as fdst:
       dstMap = json.load(fdst)
   
    allWords = [] 
    common.dvtextutils.extractWordsFromEntryMap(allWords, srcMap)
    allWords.sort()
    allSet = set(allWords)
    newMap = common.dvtextutils.separateWordsInSetWithNativeFilter(allSet, dstMap, enrichEngine)
    res = len(newMap)
    if stage< 2:
        with open(folder + 'allWords_'+lang+'.json', 'w', encoding='utf8') as json_file:
            json.dump(sorted(allSet), json_file, ensure_ascii=False, indent=2)
        prnMap = dict(sorted(newMap.items()))    
        with open(folder + 'newWords_'+lang+'.json', 'w', encoding='utf8') as json_file1:
            json.dump(prnMap, json_file1, ensure_ascii=False, indent=2)
    if stage==0 or stage==2:
       newDstMap = common.dvtextutils.populateOrigMapWithNewMap(dstMap, newMap)
       common.dvlib.saveJsonWithBackup(newDstMap, dst)

print(f"enriching single dictionary successfully finished: {res}")

