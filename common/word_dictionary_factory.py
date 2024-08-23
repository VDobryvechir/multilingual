from norskbok.norsk_word_dictionary import NorskWordDictionary 


class WordDictionaryFactory:

     @staticmethod
     # returns instances implementing the interface WordDictionary
     def create_instance(lang, folder, options):
         match lang:
            case "nb":
               return NorskWordDictionary(lang, folder, options)
            case "nn":
               return NorskWordDictionary(lang, folder, options)
            case _:
               raise Exception(f"Support for {lang} is not implemented yet")
