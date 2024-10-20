import common.dvtextutils, common.dvhtmlutils
from norskbok.id_dictionary import contentIdDictionary
from common import *
lang="nb"
fileName="C:/Volodymyrvd/python/polyglot/dictionary/mono/m_nb.json"
resFileName="C:/Volodymyrvd/python/polyglot/dictTest/unknown.txt"
pref="unknown_"
beforeEntry = "    \""
afterEntry = "\": \"\",\n"
isPrefixed = False
cnt, words = common.dvtextutils.foundAllEntriesWithPrefixInFile(fileName, resFileName, pref, beforeEntry, afterEntry, isPrefixed)
print(f"found {cnt} entries")
resFileName="C:/Volodymyrvd/python/polyglot/dictTest/unknown.html"
words = common.dvtextutils.excludeWordsByDictionary(words, contentIdDictionary, pref, {"EmptyAccepted": False })
common.dvhtmlutils.recordAllEntriesWithSearchResultsInHtml(config, fileName, resFileName, words, lang, {"OnlyOnce": True, "WholeWord": True, "Colorify": True})

  