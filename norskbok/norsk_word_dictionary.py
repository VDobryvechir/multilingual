from common.word_dictionary import WordDictionary, WordDictionaryMode 
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
        self.options = options["nb"]
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
                        if word!=sw and containWholeWord(sw, word):
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


def containWholeWord(sw, word):
    pos=0
    n=len(sw)
    m=len(word)
    while pos<n:
       npos = sw.find(word, pos)
       if npos<0:
           return False
       if npos+m==n or sw[npos+m]==" ":
           return True
       pos = npos+1  
    return False

