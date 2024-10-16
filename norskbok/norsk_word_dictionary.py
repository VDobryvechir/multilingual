from common.word_dictionary import WordDictionary, WordDictionaryMode 
import common.dvtextutils
import json
import os
import urllib.parse


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
            with urllib.request.urlopen(artUrl) as bidUrl:
                artData=bidUrl.read().decode('utf8')
            if len(artData)==0:
                print("empty response from "+artUrl)
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
       path = self.checkWordPath(lowerCaseWord)
       if path is None:
           return None
       if not os.path.exists(path):
          common.dvlib.reportError(errorFileName, f"path {path} for {lowerCaseWord} reported but does not exist")
          return None    
       with open(path, encoding='utf-8') as fdata:
          general = json.load(fdata)
       form = [] if "form" not in general else general["form"]
       data = [] if "data" not in general else general["data"]
       if len(data)==0 and len(form)==0:
          return None
       res = {'gender': '', 'description': '', 'declination': {}, 'deepDescription': ''}      
       for formItem in form:
           self.add_by_form(formItem, res, errorFileName)
       for dataItem in data:
           self.add_by_data(dataItem, res, errorFileName)
       return res  

    def add_by_form(self, word, res, errorFileName):
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
           self.add_by_data(dataItem, res, errorFileName)

    def add_by_data(self, nmb, res, errorFileName):
       path = self.checkNOarticleByNumber(nmb)
       if path is None or path=="":
          common.dvlib.reportError(errorFileName, f"path {path} for {nmb} reported but does not exist!!")
          return
       with open(path, encoding='utf-8') as fdata:
          d = json.load(fdata)
       if "body" in d and "definitions" in d["body"]:
          self.processBodyDefinitions(d["body"]["definitions"],res,errorFileName)
       if "lemmas" in d:
          for lemma in d["lemmas"]:
             if "inflection_class" in lemma:
                common.dvtextutils.addNonRepeatedMapField(res,"gender",self.analyzeGender(lemma["inflection_class"]), " ")
             if "paradigm_info" in lemma:
                 for paradigm in lemma["paradigm_info"]:
                     if "inflection" in paradigm:
                        common.dvtextutils.addNonRepeatedNamedMapField(res,"declination",self.analyzeInflection(paradigm["inflection"]), ",")   

    def analyzeGender(self, inflection):
        match inflection:
          case "verb":
            return ["vr"]
          case "v1":
            return ["vr","v1"]
          case "v2":
            return ["vr","v2"]
          case "m.":
            return ["nm"]
          case "m1":
            return ["nm","m1"]
          case "n.":                                                                 
            return ["nn"]
          case "f.":
            return ["nf"]
          case "f1":
            return ["nf","f1"]
          case "n1":
            return ["nn","n1"] 
          case "n2":
            return ["nn","n2"] 
          case "n3":
            return ["nn","n3"] 
          case _:
            return ["unknown_gender_"+inflection, inflection]
    
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

    def analyzeExplanation(self, explanation):
        res = []
        self.formatContentWithItems(res, explanation)
        items = [] if "items" not in explanation else explanation["items"]
        for item in items:
            if "lemmas" in item:
               for lemma in item["lemmas"]:
                  if "lemma" in lemma and len(lemma["lemma"])>0:
                      res.append(lemma["lemma"])
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
                 t = ""                                                                         
                 for item in items:
                     if "text" in item and len(item["text"])>0:
                          t = item["text"] if len(t)==0 else t + ", " + item["text"]
                 s = s.replace("$", t)
            res.append(s)                        

