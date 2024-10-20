import common.dvtextutils, common.dvhtmlutils
from norskbok.id_dictionary import contentIdDictionary
from common import *
lang="nb"
fileName="C:/Volodymyrvd/python/polyglot/dictionary/mono/m_nb.json"
resFileName="C:/Volodymyrvd/python/polyglot/dictTest/strange.txt"
pref="strange_"
beforeEntry = "    \""
afterEntry = "\": \"\",\n"
isPrefixed = False
cnt, words = common.dvtextutils.foundAllEntriesWithPrefixInFile(fileName, resFileName, pref, beforeEntry, afterEntry, isPrefixed)
print(f"found {cnt} entries")
resFileName="C:/Volodymyrvd/python/polyglot/dictTest/strange.html"
common.dvhtmlutils.recordAllEntriesWithSearchResultsInHtml(config, fileName, resFileName, words, lang,
       {"OnlyOnce": True, "WholeWord": True, "Colorify": True, "EntryLink": True})

  