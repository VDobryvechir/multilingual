from abc import ABC, abstractmethod
from enum import IntEnum

class WordDictionaryMode(IntEnum):
    VERBOSE = 1
    DEEP_CHECK = 2

class WordDictionary:
   @abstractmethod
   #checks that all data are saved locally correct 
   #mode 0 - just for existing data
   #     1 - for all words in the dictionary
   def check_consistensy(self, mode):
       pass

   @abstractmethod
   #for nouns returns gender og just noun: fmn | s
   #for verbs returns v<group of inflection> v0, v1, v2, v3, v4 ....
   #for prepositions returns p
   #for adjectives returns a(fmnpfmn) 
   #for adverbs returns e<0, 1, 2, 3>
   #for other words returns nothing.
   #if several opportunities, it returns them all separated by space
   def grammar_specification(self):
       pass 
  
   @abstractmethod
   #return all definitions in the same language separated by semicolumn and space
   def all_definitions(self, word):
       pass    

