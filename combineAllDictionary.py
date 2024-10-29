from common import *
import common.dvtextutils, common.dvlib
import common.dvtextutils
from common.enrich_mono_dictionary import EnrichMonoDictionary

langFilter = ["nb"]
# 2 test for small data and not affecting origin
# 1 test for all data but not affecting origin
# 0 real production engine
testMode = (0, "[folder]flertall_[lang].json","[folder]mono_[lang].json")

#--------------------------------------------------------------------------------------------------------
langs = config["languages"]
for lang in langs:
    if lang not in langFilter:
        continue
    mdict = common.dvlib.loadLangFile(config["sources"]["monoDictionary"],lang)
    sdict = common.dvlib.loadLangFile(config["sources"]["multiDictionary"],lang)
    fdict = common.dvlib.loadLangFile(config["sources"]["flertallDictionary"],lang)
    adictFile = config["sources"]["allDictionary"].replace("[lang]",lang)
    count=0
    for word in sdict:
        multiEntry = sdict[word]
        count += 1
        if word in mdict:
            monoEntry = mdict[word]
            common.dvtextutils.enrichMultiWithMono(multiEntry, monoEntry, sdict, fdict)
    common.dvlib.saveJsonWithBackup(sdict,adictFile)
    print(f"combined all {lang} dictionary with {count} entries")
