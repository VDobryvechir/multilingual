from abc import ABC, abstractmethod
from enum import IntEnum

class WordDictionaryMode(IntEnum):
    VERBOSE = 1
    DEEP_CHECK = 2

class WordDictionary:
   @abstractmethod
   #checks that all data are saved locally correct 
   #mode 1 - verbose
   #     2 - deep check
   def check_consistensy(self, mode):
       pass

   @abstractmethod
   #for each word returns structure as follows:
   # gender: string
   # declination: string
   # description: string
   # deepDescription: string 
   # expression: map<string, {description:string, deepDescription: string}>
   # None if info is not available
   def mono_entry_reader(self, word, lowerCaseWord, errorFileName):
       pass 
  
   @abstractmethod
   #return list of all sources as json objects        
   def get_all_sources(self, word, lowerCaseWord, errorFileName):
       pass    

   @abstractmethod
   # word is a string to be tested
   #return True if word is native or False otherwise  
   def is_word_native(self, word):
       pass
   