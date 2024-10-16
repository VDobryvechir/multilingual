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
   # None if info is not available
   def mono_entry_reader(self, word, lowerCaseWord, errorFileName):
       pass 
  
   @abstractmethod
   #return all definitions in the same language separated by semicolumn and space
   def all_definitions(self, word):
       pass    

