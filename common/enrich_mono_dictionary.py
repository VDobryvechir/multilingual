import urllib.request, json, os, common.dvlib
import common.word_dictionary_factory

class EnrichMonoDictionary:

   def __init__(self, lang, config):
       self.lang = lang  
       self.defMonoDictFile = config["sources"]["monoDictionary"].replace("[lang]",lang)
       self.defMultiDictFile = config["sources"]["multiDictionary"].replace("[lang]",lang)      
       self.config = config
       self.dictionary = None

   def getWordDictionary(self):
       if self.dictionary is not None:
            return self.dictionary
       folder = self.config["sources"]["ordbok"]
       options = self.config["ordbok"][self.lang]
       dictionary = common.word_dictionary_factory.WordDictionaryFactory.create_instance(self.lang, folder, options)
       self.dictionary = dictionary
       return dictionary

   def processDefault(self):
       return self.processEnrichment(self.defMonoDictFile, self.defMultiDictFile)

   def isWordNative(self, word):
       dictionary = self.getWordDictionary()
       return dictionary.is_word_native(word)
   
   def getWordSources(self, word):
       errorFileName = self.defMonoDictFile + "_error"
       lowerCaseWord = word.lower()
       dictionary = self.getWordDictionary()
       res = dictionary.get_all_sources(word, lowerCaseWord, errorFileName)
       return res

   def processEnrichment(self, monoDictFile, multiDictFile):
       dictionary = self.getWordDictionary()
       with open(monoDictFile, encoding='utf-8') as fmonoDictFile:
          monoData = json.load(fmonoDictFile)
       with open(multiDictFile, encoding='utf-8') as fmultiDictFile:
          multiData = json.load(fmultiDictFile)
       monoSize = len(monoData)
       multiSize = len(multiData)
       multiNew = common.dvlib.findMapNewWords(multiData, monoData)
       multiNewSize = len(multiNew)
       print(f"copy from {multiDictFile} [{multiSize}] to {monoDictFile} [{monoSize}], total {multiNewSize} ")
       monoAdded = 0
       monoMissed = 0
       missFileName = monoDictFile + "_missed"
       errorFileName = monoDictFile + "_error"
       missData = common.dvlib.readMapFromFileIfExists(missFileName)
       for word in multiNew:
          orig = word
          if "or" in multiData[word]:
             orig = multiData[word]["or"]     
          entry = dictionary.mono_entry_reader(orig, word, errorFileName)
          if entry is None:
              monoMissed += 1
              missData[word] = {'gender':'','declination':'','description':'','deepDescription':''}
          else:
              monoAdded += 1
              monoData[word] = entry
  
       if monoAdded > 0:
          monoData = dict(sorted(monoData.items()))  
          common.dvlib.saveJsonWithBackup(monoData, monoDictFile) 
       if monoMissed>0:
          missData = dict(sorted(missData.items()))  
          common.dvlib.saveJsonWithBackup(missData, missFileName) 
       res = f" total {multiNewSize}, added {monoAdded}, missed {monoMissed}"
       return res
