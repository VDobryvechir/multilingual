from common import *
import common.dvoversetlib

testMode = True
srcLang="nb"
dstLang="en"
batchSize=400 if not testMode else 2
limitation=1000000
fileName = config["sources"]["testFolder"]+"multi_[lang].json" if testMode else config["sources"]["multiDictionary"]

res = common.dvoversetlib.manageBulkTranslate(srcLang, dstLang, batchSize, limitation, config, fileName)
print(res)
