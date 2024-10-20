from common.word_dictionary import WordDictionary, WordDictionaryMode 
import common.dvtextutils
import json
import os
import urllib.parse
from norskbok.id_dictionary import contentIdDictionary 

class NorskWordDictionary(WordDictionary):

    def __init__(self, lang, folder, options):
        self.lang = lang
        self.folder = folder
        self.inner_lang = options[f"innen_{lang}"]
        self.verbose = False
        self.deepcheck = False
        self.options = options
        self.ref1 = self.options["ref1"].replace("{lang}", self.inner_lang) 
        self.ref2 = self.options["ref2"].replace("{lang}", self.inner_lang)
        self.ref3 = self.options["ref3"].replace("{lang}", self.inner_lang)

    def check_consistensy(self, mode):
        self.verbose = (mode & WordDictionaryMode.VERBOSE) != 0
        self.deepcheck = (mode & WordDictionaryMode.DEEP_CHECK) != 0
        self.checkWordPath("eierne")  
        print(f"checking consistency {self.lang}  mode {mode} in {self.folder}")
    

    def getNOArticlePath(self, nmb):
        n=len(nmb)
        sub = "0" if n<4 else nmb[0:n-3]
        directory = self.folder + "a_" + self.lang + "/" + sub
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory + "/" + nmb + ".json"
                
    def checkNOarticleByNumber(self, nmb):
        fpath = self.getNOArticlePath(nmb)
        if not os.path.exists(fpath):
            artUrl = self.ref1.replace("{nmb}", nmb) 
            try:
               with urllib.request.urlopen(artUrl) as bidUrl:
                   artData=bidUrl.read().decode('utf8')
            except Exception:
               print(f"Error requesting {artUrl}")
               return None
            if len(artData)==0:
                print(f"empty response from {artUrl}")
                return None
            else:  
                with open(fpath, 'w', encoding='utf8') as art_file:
                    art_file.write(artData)
        return fpath

    def extractArticleData(self, word):
        wrd = urllib.parse.quote_plus(word) 
        url = self.ref2.replace("{wrd}", wrd)
        with urllib.request.urlopen(url) as bidUrl:
            artData=json.load(bidUrl)
        res=[]    
        if ("articles" in artData) and (self.inner_lang in artData["articles"]):
            p=artData["articles"][self.inner_lang]
            for iNmb in p:
                sNmb = str(iNmb)
                self.checkNOarticleByNumber(sNmb)
                res.append(sNmb)
        return res

    def extractArticleSuggestions(self, word):
        wrd = urllib.parse.quote_plus(word) 
        url = self.ref3.replace("{wrd}", wrd)
        with urllib.request.urlopen(url) as bidUrl:
            artData=json.load(bidUrl)
        res={}    
        if ("a" in artData):
            if "exact" in artData["a"]:
                p=artData["a"]["exact"]
                phrase=[]  
                for item in p:
                    if len(item)>0:
                        sw=item[0]
                        print(sw)
                        if word!=sw and common.dvtextutils.containWholeWord(sw, word):
                            phrase.append(sw)
                if len(phrase)>0:
                    res["phrase"]=phrase
            if "inflect" in artData["a"]:
                p=artData["a"]["inflect"]
                frm=[]  
                for item in p:
                    if len(item)>0:
                        sw=item[0]
                        if len(sw)>0:
                            frm.append(sw)
                if len(frm)>0:
                    res["form"]=frm
        return res

    def getWordPath(self, word):
        word = word.lower()
        sub = (word + "_")[0:2]
        directory = self.folder + self.lang + "/" + sub
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory + "/" + word + ".json"
    
    def checkWordPath(self, word):
        fpath=self.getWordPath(word)
        if os.path.exists(fpath):
            if self.verbose:
                print(f"word {word} already exists in folder {fpath}")
            return fpath
        res1=self.extractArticleData(word)
        res2=self.extractArticleSuggestions(word)
        if self.verbose:
            print(f"word {word} loaded thru {res1} and {res2} saved in {fpath}")  
        res2["data"]=res1
        with open(fpath, 'w', encoding='utf8') as json_file:
            json.dump(res2, json_file, ensure_ascii=False, indent=2)
        return fpath    

    def mono_entry_reader(self, word, lowerCaseWord, errorFileName):
       data, n = self.get_all_source_indices(word, lowerCaseWord, errorFileName)
       if data is None:
           return None
       res = {'gender': '', 'description': '', 'declination': {}, 'deepDescription': ''}
       
       for index, dataItem in enumerate(data):
           if not self.add_by_data(dataItem, res, errorFileName, index < n, lowerCaseWord):
              return None
       return res  

    def get_all_source_indices(self, word, lowerCaseWord, errorFileName):
       path = self.checkWordPath(lowerCaseWord)
       if path is None:
           return (None, 0)
       if not os.path.exists(path):
          common.dvlib.reportError(errorFileName, f"path {path} for {lowerCaseWord} reported but does not exist")
          return (None, 0)    
       with open(path, encoding='utf-8') as fdata:
          general = json.load(fdata)
       form = [] if "form" not in general else general["form"]
       data = [] if "data" not in general else general["data"]
       n = len(data)
       if n==0 and len(form)==0:
          return (None, 0)
       for formItem in form:
           self.add_by_form(formItem, errorFileName, data)
       return (data, n)
       
    def get_all_sources(self, word, lowerCaseWord, errorFileName):
       res = []
       data, _ = self.get_all_source_indices(word, lowerCaseWord, errorFileName)
       if data is None:
           return res
       for nmb in data:
           path = self.checkNOarticleByNumber(nmb)
           if path is None or path=="":
              common.dvlib.reportError(errorFileName, f"path {path} for {nmb} reported but does not exist!!")
              return res
           with open(path, encoding='utf-8') as fdata:
              d = json.load(fdata)
           res.append(d)           
       return res 

    def add_by_form(self, word, errorFileName, dataPool):
       path = self.checkWordPath(word)
       if path is None:
           common.dvlib.reportError(errorFileName, f"no word for {word} but reported as the existing word")
           return
       if not os.path.exists(path):
          common.dvlib.reportError(errorFileName, f"path {path} for {word} reported but does not exist!")
          return    
       with open(path, encoding='utf-8') as fdata:
          general = json.load(fdata)
       data = [] if "data" not in general else general["data"]
       if len(data)==0:
          common.dvlib.reportError(errorFileName, f"data at {path} for {word} missed, but expected to exist!")
          return
       for dataItem in data:
           dataPool.append(dataItem)

    def add_by_data(self, nmb, res, errorFileName, isPrimary, wordLower):
       path = self.checkNOarticleByNumber(nmb)
       if path is None or path=="":
          common.dvlib.reportError(errorFileName, f"path for word {wordLower} for {nmb} reported but does not exist!!")
          return False
       with open(path, encoding='utf-8') as fdata:
          d = json.load(fdata)
       if "lemmas" in d:
          for lemma in d["lemmas"]:
             if "paradigm_info" in lemma:
                 declMap = {} if "declination" not in res or res["declination"] is None else res["declination"].copy() 
                 preliminary = {"declination": declMap}
                 for paradigm in lemma["paradigm_info"]:
                     if "inflection" in paradigm:
                        common.dvtextutils.addNonRepeatedNamedMapField(preliminary,"declination",self.analyzeInflection(paradigm["inflection"]), ",")
                 if isPrimary or common.dvtextutils.containDictionaryWholeLowerWord(preliminary["declination"], wordLower):
                    isPrimary = True          
                    res["declination"] = preliminary["declination"]
             if isPrimary and "inflection_class" in lemma:
                common.dvtextutils.addNonRepeatedMapField(res,"gender",self.analyzeGender(lemma["inflection_class"]), " ")
       if isPrimary and "body" in d and "definitions" in d["body"]:
          self.processBodyDefinitions(d["body"]["definitions"],res,errorFileName)
       return True   

    def analyzeGender(self, inflection):
        if inflection is None or len(inflection)==0:
            return []
        infl = inflection if isinstance(inflection, str) else "strange_type_" + type(inflection).__name__
        infl = infl.replace(",", "").strip()
        if " " in infl:
            ar = infl.split(" ")
            res = []
            for item in ar:
                cur = self.analyzeGender(item)
                res = res + cur
            return res    
        match infl:
          case "verb":
            return ["vr"]
          case "v1":
            return ["vr","v1"]
          case "v2":
            return ["vr","v2"]
          case "v2verb":
            return ["vr","v2"]
          case "v3":
            return ["vr","v3"]
          case "v4":
            return ["vr","v4"]
          case "m.":
            return ["nm"]
          case "m1":
            return ["nm","m1"]
          case "m2":
            return ["nm","m2"]
          case "m3":
            return ["nm","m3"]
          case "n.":                                                                 
            return ["nn"]
          case "f.":
            return ["nf"]
          case "f1":
            return ["nf","f1"]
          case "f1m1":
            return ["nf","f1","nm","m1"]   
          case "f.m.n.":
            return ["nf","nm","nn"]   
          case "f.m.":
            return ["nf","nm"]   
          case "m.m2n.":
            return ["nm","m_","m2","nn"]   
          case "m.m1":
            return ["nm","m_","m1"]   
          case "m1n.":
            return ["nm","nn","m1"]   
          case "n1":
            return ["nn","n1"] 
          case "n2":
            return ["nn","n2"] 
          case "n3":
            return ["nn","n3"]
          case "a1":
            return ["adj", "a1"]      
          case "a2":
            return ["adj", "a2"]      
          case "a2a3":
            return ["adj", "a2","a3"]      
          case "a3":
            return ["adj", "a3"]      
          case "a4":
            return ["adj", "a4"]      
          case "a5":
            return ["adj", "a5"]      
          case _:
            return ["unknown_gender_"+infl, infl]
    
    def analyzeInflection(self, inflection):
        res={}
        for inflect in inflection:
          if "tags" in inflect and "word_form" in inflect:
             key="-".join(inflect["tags"]).replace("<","").replace(">","").replace("/","_")
             s = inflect["word_form"]
             if s is not None and len(s)>0:
                res[key] = s
        return res
    
    def processBodyDefinitions(self,definitions,res,errorFileName):
        for definition in definitions:
            self.processBodyDefinition(definition,res,errorFileName)

    def processBodyDefinition(self,definition,res,errorFileName):
        if "elements" in definition and len(definition["elements"])>0:
            for element in definition["elements"]:
                if "type_" in element:
                    match element["type_"]:
                       case "explanation":
                           common.dvtextutils.addNonRepeatedMapField(res,"description",self.analyzeExplanation(element), ";")
                       case "example":
                           quote = {} if "quote" not in element else element["quote"]
                           explanation = {} if "explanation" not in element else element["explanation"]
                           common.dvtextutils.addNonRepeatedMapField(res,"deepDescription",self.analyzeExample(quote, explanation), ";")
                       case "definition":
                           self.processBodyDefinition(element,res,errorFileName)
                       case "sub_article":
                           common.dvtextutils.addDictionaryMapField(res,"expression",self.analyzeArticle(element,errorFileName), ";") 

    def analyzeArticle(self,element,errorFileName):
        res = {} 
        if "lemmas" in element and "article" in element and "body" in element["article"]:
            s = ", ".join(element["lemmas"])
            t = element["article"]["body"]
            if "definitions" in t: 
                val={}
                self.processBodyDefinitions(t["definitions"],val,errorFileName)
                res[s]=val  
        return res    

    def analyzeExplanation(self, explanation):
        res = []
        self.formatContentWithItems(res, explanation)
        return res
    
    def analyzeExample(self, quote, explanation):
        res = []
        self.formatContentWithItems(res, quote)                                        
        self.formatContentWithItems(res, explanation)
        return res

    def formatContentWithItems(self, res, block): 
        if len(block)>0 and "content" in block and len(block["content"])>0:
            s = block["content"]
            n = s.find("$")
            items = [] if "items" not in block else block["items"]
            if n>=0 and len(items)>0:
                 for item in items:
                     p = "strange_"
                     if "text" in item and len(item["text"])>0:
                          p = item["text"]
                     elif "id" in item:
                          pp = item["id"]
                          if pp in contentIdDictionary:
                             p = contentIdDictionary[pp]
                          else:
                             p = "unknown_" + pp            
                     elif "denominator" in item and "numerator" in item:
                        denominator = item["denominator"]
                        numerator = item["numerator"]
                        if numerator==1:    
                            p = str(numerator)+" del av " + str(denominator)
                        else:
                           p = str(numerator)+" deler av " + str(denominator)           
                     elif "lemmas" in item:
                         for lemma in item["lemmas"]:
                            if "lemma" in lemma and len(lemma["lemma"])>0:
                                p = lemma["lemma"]
                                p = p.replace("$", "_")
                                s = s.replace("$", p, 1)
                         continue 
                     elif "content" in item:
                         newRes = []
                         self.formatContentWithItems(newRes, item)
                         p = "" if len(newRes)==0 else newRes[0]
                     p = p.replace("$", "_")
                     s = s.replace("$", p, 1)
            if len(s)>0:         
                res.append(s)                        

    # word is a string to be tested
    #return True if word is native or False otherwise  
    def is_word_native(self, word):
        kd = ord("ø")
        n = len(word)
        if n==0:
           return False
        for w in word:
           if ord(w)>kd:
              return False
        return True
    
