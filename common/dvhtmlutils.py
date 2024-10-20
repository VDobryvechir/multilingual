
from common.enrich_mono_dictionary import EnrichMonoDictionary
from common.dvtextutils import *
import json

htmlJsSupport=r"""
<style>
pre {outline: 1px solid #ccc; padding: 5px; margin: 5px; }
.string { color: green; }
.number { color: darkorange; }
.boolean { color: blue; }
.null { color: magenta; }
.key { color: red; }
#main {display:flex;}
h2 {cursor:pointer;}
.cross{background-color:blue;color:yellow;display:inline-block;padding:5px;border-radius:4px;font-size:140%;}
</style>
<script>
function output(inp) {
    document.getElementById("jsblock").appendChild(document.createElement('pre')).innerHTML = inp;
}
function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}
function setShow(word) {
    document.getElementById("content").style.width = "50vw";
    const el = document.getElementById("jsblock");
    el.innerHTML = "";
    el.style.width="50vw";
    el.style.padding="5px";
    const obj = jsdata[word];
    if (obj) {
        const str = JSON.stringify(obj, undefined, 4);
        output(syntaxHighlight(str));
    } 
}
</script>
<div id="main">
   <div id="content">
"""
htmlJsSupportEnd="""
   </div>
   <div id="jsblock">
   </div>
</div>
<script>
const jsdata=
"""
htmlJsSupportFinal="""
;</script>
"""
def recordAllEntriesWithSearchResultsInHtml(config, srcFileName, dstFileName, words, lang, options):
    with open(srcFileName, encoding='utf-8') as fSrc:
        src = json.load(fSrc)
    dst = htmlJsSupport
    onlyOnce = False if "OnlyOnce" not in options else options["OnlyOnce"]
    wholeWords = False if "WholeWord" not in options else options["WholeWord"]
    colorify = False if "Colorify" not in options else options["Colorify"]
    sources = {}
    enrichEngine = EnrichMonoDictionary(lang, config)
    for word in words:
        dst += "<h1>" + word + "</h1>\n"
        entries = searchAllEntriesInDictionary(src, word, onlyOnce, wholeWords)
        for entry in entries:
            sources[entry]=enrichEngine.getWordSources(entry);
            dst += "<h2>" + getDictionaryLink(entry) + "<span class='cross' onclick=\"setShow('"+entry+"')\">+</span></h2>\n<div>\n"
            txt = json.dumps(entries[entry], ensure_ascii=False)
            if colorify:
                txt = highlightenWords(txt, word, "<span style='color:red'>","</span>")
            dst += txt
            dst += "\n</div>\n"
    dst += htmlJsSupportEnd + json.dumps(sources, ensure_ascii=False) + htmlJsSupportFinal
    with open(dstFileName, "w", encoding='utf-8') as file:
        file.write(dst)
