from common import *
import common.word_dictionary_factory
from common.word_dictionary import WordDictionaryMode

langFilter = ["nb"]

#--------------------------------------------------------------------------------------------------------
langs = config["languages"]
folder = config["sources"]["ordbok"]
options = config["ordbok"]
for lang in langs:
    if lang not in langFilter:
        continue
    dictionary = common.word_dictionary_factory.WordDictionaryFactory.create_instance(lang, folder, options)
    dictionary.check_consistensy(WordDictionaryMode.VERBOSE + WordDictionaryMode.DEEP_CHECK) 
print("fixing word dictionary successfully finished")

