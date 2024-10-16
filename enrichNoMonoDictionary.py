from common import *
from common.enrich_mono_dictionary import EnrichMonoDictionary

langFilter = ["nb"]
testMode = (True, "[folder]multi_[lang].json","[folder]mono_[lang].json")

#--------------------------------------------------------------------------------------------------------
langs = config["languages"]
for lang in langs:
    if lang not in langFilter:
        continue
    enrichEngine = EnrichMonoDictionary(lang, config)
    if testMode[0]:
       folder = config["sources"]["testFolder"]
       multi = testMode[1].replace("[lang]",lang).replace("[folder]",folder)
       mono = testMode[2].replace("[lang]",lang).replace("[folder]",folder)
       res = enrichEngine.processEnrichment(mono, multi)    
    else:
       res = enrichEngine.processDefault()
print(f"enriching word dictionary successfully finished: {res}")

