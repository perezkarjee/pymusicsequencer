# -*- coding: utf8 -*-

otNames = [u"창세기",  u"출애굽기",  u"레위기",  u"민수기",  u"신명기",  u"여호수아",  u"사사기",  u"룻기",  u"사무엘상",  u"사무엘하",  u"열왕기상",  u"열왕기하",  u"역대상",  u"역대하",  u"에스라",  u"느헤미야",  u"에스더",  u"욥기",  u"시편",  u"잠언",  u"전도서",  u"아가",  u"이사야",  u"예레미야",  u"예레미야애가",  u"에스겔",  u"다니엘",  u"호세아",  u"요엘",  u"아모스",  u"오바댜",  u"요나",  u"미가",  u"나훔",  u"하박국",  u"스바냐",  u"학개",  u"스가랴",  u"말라기", ] 


ntNames = [u"마태복음",  u"마가복음",  u"누가복음",  u"요한복음",  u"사도행전",  u"로마서",  u"고린도전서",  u"고린도후서",  u"갈라디아서",  u"에베소서",  u"빌립보서",  u"골로새서",  u"데살로니가전서",  u"데살로니가후서",  u"디모데전서",  u"디모데후서",  u"디도서",  u"빌레몬서",  u"히브리서",  u"야고보서",  u"베드로전서",  u"베드로후서",  u"요한일서",  u"요한이서",  u"요한삼서",  u"유다서",  u"요한계시록"]

import codecs
import sys
f = codecs.open("./easy_bible.txt", "r", "utf-8")
text = f.read()
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
        if firstFound != chapterNameShort:
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
        verse = txt[numberLast:]

        chapterVerse = txt[chapterNameIdx:numberLast].split(u":")
        chapterNum = int(chapterVerse[0])
        verseNum = int(chapterVerse[1])
        if chapterNum != curChapterNum:
            curBook += [curChapter]
            curChapterNum += 1
            curChapter = []

        curChapter += [verse]
print bible[-1][-1][-1]
