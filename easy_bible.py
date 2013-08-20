# -*- coding: utf8 -*-
NEWHANGUL = 1
EASYBIBLE = 2
NLT = 3
mode = NLT


import codecs
import sys
otNames = [u"창세기",  u"출애굽기",  u"레위기",  u"민수기",  u"신명기",  u"여호수아",  u"사사기",  u"룻기",  u"사무엘상",  u"사무엘하",  u"열왕기상",  u"열왕기하",  u"역대상",  u"역대하",  u"에스라",  u"느헤미야",  u"에스더",  u"욥기",  u"시편",  u"잠언",  u"전도서",  u"아가",  u"이사야",  u"예레미야",  u"예레미야애가",  u"에스겔",  u"다니엘",  u"호세아",  u"요엘",  u"아모스",  u"오바댜",  u"요나",  u"미가",  u"나훔",  u"하박국",  u"스바냐",  u"학개",  u"스가랴",  u"말라기", ] 
ntNames = [u"마태복음",  u"마가복음",  u"누가복음",  u"요한복음",  u"사도행전",  u"로마서",  u"고린도전서",  u"고린도후서",  u"갈라디아서",  u"에베소서",  u"빌립보서",  u"골로새서",  u"데살로니가전서",  u"데살로니가후서",  u"디모데전서",  u"디모데후서",  u"디도서",  u"빌레몬서",  u"히브리서",  u"야고보서",  u"베드로전서",  u"베드로후서",  u"요한일서",  u"요한이서",  u"요한삼서",  u"유다서",  u"요한계시록"]
names = otNames + ntNames

if mode == NEWHANGUL:
    f = codecs.open(u"./개역한글판성경.txt", "r", "cp949")
elif mode == EASYBIBLE:
    f = codecs.open("./easy_bible.txt", "r", "utf-8")
elif mode == NLT:
    f = codecs.open("./NLT.txt", "r", "cp949")
text = f.read()
f.close()
text = text.split("\n")

firstFound = u"창"
curChapterNum = 1
bible = [] # book1, book2
curChapter = [] # verse1, verse2
curBook = [] # chapter1, chapter2
for txt in text:
    if u":" in txt:
        chapterNameIdx = 0
        for chara in txt:
            if 48 <= ord(chara) <= 57:
                break
            chapterNameIdx += 1

        chapterNameShort = txt[:chapterNameIdx]
        chapterNameShort = chapterNameShort.strip(" ")
        if firstFound != chapterNameShort:
            firstFound = chapterNameShort
            curBook += [curChapter]
            bible += [curBook]
            curBook = []
            curChapter = []
            curChapterNum = 1

        numberLast = chapterNameIdx
        for chara in txt[chapterNameIdx:]:
            if not (48 <= ord(chara) <= 57 or chara == u":"):
                break
            numberLast += 1
        if mode == NLT:
            verse = txt[numberLast+2:]
        else:
            verse = txt[numberLast:]

        chapterVerse = txt[chapterNameIdx:numberLast].split(u":")
        chapterNum = int(chapterVerse[0])
        verseNum = int(chapterVerse[1])
        if chapterNum != curChapterNum:
            curBook += [curChapter]
            curChapterNum += 1
            curChapter = []

        curChapter += [verse]

bible += [curBook]

indexHeader = u"""\
<html>
<head>
<style>
body
{
    font-size: 80%%;
    font-family:Arial,Helvetica,sans-serif;
    line-height: 200%%;
    color: #453804;
    
background-color:#CACABE;
}
div.hr {
  height: 3px;
  background: #363427;
}
div.hr hr {
  display: none;
}

A:link{text-decoration:none; color:#594805;}
A:visited{text-decoration:none; color:#097067;}
A:active{text-decoration:none; color:#591E05;}
A:hover{text-decoration:underline; color:#594805;}
h1 { color: #363427;}
h2 { color: #363427;}
h3 { color: #363427;margin-bottom:0px;}
</style>

<meta http-equiv="Content-Type" content="text/html; charset=utf8">
<title>%s</title>
</head>
<body>
<h1>
%s
</h1>
"""
header = u"""\
<html>
<head>
<style>
body
{
    font-size: 80%%;
    font-family:Arial,Helvetica,sans-serif;
    line-height: 120%%;
    color: #453804;
    margin:0;
    padding:0;
    word-wrap:break-word; 
    
background-color:#CACABE;
}
div.hr {
  height: 3px;
  background: #363427;
}
div.hr hr {
  display: none;
}

A:link{text-decoration:none; color:#594805;}
A:visited{text-decoration:none; color:#097067;}
A:active{text-decoration:none; color:#591E05;}
A:hover{text-decoration:underline; color:#594805;}
h1 { color: #363427;}
h2 { color: #363427;}
h3 { color: #363427;margin-bottom:0px;}

#wrap {
width:950px;
margin:0 auto;
padding:10px;
background:#CACABE;
}
#header {
padding:5px 10px;
background:#CACABE;
}
#nav {
padding:5px 10px;
background:#CACABE;
}
#main {
float:left;
width:700px;
background:#CACABE;
}
#sidebar {
float:right;
padding:10px;
width:200px;
background:#CACABE;
}
#sidebarF {
    line-height: 180%%;
position:fixed;
top: 20px;
width:165px;
};
#footer {
clear:both;
padding:5px 10px;
background:#CACABE;
}
* html #footer {
height:1px;
}


</style>

<meta http-equiv="Content-Type" content="text/html; charset=utf8">
<title>%s</title>
</head>
<body>
<div id="wrap">
<div id="header">
    <h1>
    %s
    </h1>
</div>
<div id="nav"></div>
<div id="main">

"""
footer = u"""\
</div>
<div id="sidebar"><div id="sidebarF">
%s<br/>
<a href="index.html">목록으로</a><br/>
%s
</div></div>
</div>
</body>
</html>
"""
indexFooter = u"""\
</body>
</html>
"""

if mode == NEWHANGUL:
    indexFile = codecs.open("./newhangul/index.html", "w", "utf-8")
    indexFile.write(indexHeader % (u"개역한글 성경", u"개역한글 성경"))
elif mode == EASYBIBLE:
    indexFile = codecs.open("./easy_bible/index.html", "w", "utf-8")
    indexFile.write(indexHeader % (u"쉬운 성경", u"쉬운 성경"))
elif mode == NLT:
    indexFile = codecs.open("./nlt/index.html", "w", "utf-8")
    indexFile.write(indexHeader % (u"New Living Translation", u"New Living Translation"))
indexFile.write(u"<h2>구약 성경</h2>")
indexFile.write(u"<div class=\"hr\"><hr/></div>")

bookNum = 1
for book in bible:
    isNT = bookNum > len(otNames)
    if not isNT:
        oldNewStr = u"Old Testament"
    else:
        oldNewStr = u"New Testament"

    if bookNum == len(otNames)+1:
        indexFile.write(u'''<h2>신약성경</h2>''')
        indexFile.write(u"<hr/>")

    chapterNum = 1
    indexFile.write(u'''<h3>%s</h3>''' % (names[bookNum-1]))
    menuItem = []

    for chapter in book: # EASYKOREAN - Old Testament - 창세기 - 1장.html
        if mode == NEWHANGUL:
            fileName = u"NEWHANGUL KOREAN - %s - %s - %d.html" % (oldNewStr, names[bookNum-1], chapterNum)
        elif mode == EASYBIBLE:
            fileName = u"EASYBIBLE KOREAN - %s - %s - %d.html" % (oldNewStr, names[bookNum-1], chapterNum)
        elif mode == NLT:
            fileName = u"New Living Translation - %s - %s - %d.html" % (oldNewStr, names[bookNum-1], chapterNum)

        menuItem += [u'''<a href="%s">%s</a> ''' % (fileName, `chapterNum`+u"장")]
        if not (chapterNum % 4):
            menuItem += [u"<br/>"]
        chapterNum += 1

    chapterNum = 1
    for chapter in book: # EASYKOREAN - Old Testament - 창세기 - 1장.html
        if mode == NEWHANGUL:
            fileName = u"NEWHANGUL KOREAN - %s - %s - %d.html" % (oldNewStr, names[bookNum-1], chapterNum)
            f = codecs.open("./newhangul/NEWHANGUL KOREAN - %s - %s - %d.html" % (oldNewStr, names[bookNum-1], chapterNum), "w", "utf-8")
        elif mode == EASYBIBLE:
            fileName = u"EASYBIBLE KOREAN - %s - %s - %d.html" % (oldNewStr, names[bookNum-1], chapterNum)
            f = codecs.open("./easy_bible/EASYBIBLE KOREAN - %s - %s - %d.html" % (oldNewStr, names[bookNum-1], chapterNum), "w", "utf-8")
        elif mode == NLT:
            fileName = u"New Living Translation - %s - %s - %d.html" % (oldNewStr, names[bookNum-1], chapterNum)
            f = codecs.open("./nlt/New Living Translation - %s - %s - %d.html" % (oldNewStr, names[bookNum-1], chapterNum), "w", "utf-8")

        indexFile.write(u'''<a href="%s">%s</a> ''' % (fileName, `chapterNum`+u"장"))

        verseNum = 1

        windowTitle = u"%s %d장" % (names[bookNum-1], chapterNum)
        f.write(header % (windowTitle, windowTitle)) # 창세기 1장
        #f.write(prevNext)
        #f.write(chapterLinks)

        for verse in chapter:
            f.write(u"%d절 " % verseNum)
            f.write(verse)
            f.write("<br/><br/>")
            verseNum += 1

        f.write(footer % (windowTitle, " ".join(menuItem)))
        chapterNum += 1
        f.close()
    print u"%d/%d" % (bookNum, len(bible))
    bookNum += 1
indexFile.close()
