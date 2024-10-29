from common import *
import common.dvoversetlib

testMode = True
srcLang="nb"
dstLang="en"
batchSize=1000 if not testMode else 2
limitation=1000000
fileName = config["sources"]["testFolder"]+"flertall_[lang].json" if testMode else config["sources"]["flertallDictionary"]

res = common.dvoversetlib.manageBulkTranslate(srcLang, dstLang, batchSize, limitation, config, fileName)
print(res)
