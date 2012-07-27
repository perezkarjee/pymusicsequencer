# -*- coding: utf8 -*-
"""
DigDigRPG
Copyright (C) 2011 Jin Ju Yu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# XXX:현재 장소에서 다음에 올 수 있는 모든 목록을 만든다. 모든 목록을 두고 불가능한 것을 제거하는 방식으로 만든다.
# 그것을 어떤 테이블로 만들어 소스를 간략화한다.
# 예를들어 2글자짜리를  [모든리스트] -> [모든리스트2]를 두고 모든리스트의 하나를 골라 모든리스트2에서 올 수 있는
# 것만 빼고 모두 지워 리스트를 만든다. 그 리스트를 걍 데이터로 저장해두고 읽어서 쓴다.
# 자음
# 모음
# 자음자음
# 자음모음
# 모음자음
# 모음모음
# 이런식으로 한다.
# TODO: 한자입력. 특수문자 입력.
#
chosung = ['r','R','s','e','E','f','a','q','Q','t','T','d','w','W','c','z','x','v','g']
jungsung = ['k','o','i','O','j','p','u','P','h','hk','ho','hl','y','n','nj','np','nl','b','m','ml','l']
jongsung = [None,'r','R','rt','s','sw','sg','e','f','fr','fa','fq','ft','fx','fv','fg','a','q','qt','t','T','d','w','c','z','x','v','g']

singlesStr2Uni = {
    "r": u"ㄱ",
    "R": u"ㄲ",
    "rt": u"ㄳ",
    "s": u"ㄴ",
    "sw": u"ㄵ",
    "sg": u"ㄶ",
    "e": u"ㄷ",
    "E": u"ㄸ",
    "f": u"ㄹ",
    "fr": u"ㄺ",
    "fa": u"ㄻ",
    "fq": u"ㄼ",
    "ft": u"ㄽ",
    "fx": u"ㄾ",
    "fv": u"ㄿ",
    "fg": u"ㅀ",
    "a": u"ㅁ",
    "q": u"ㅂ",
    "Q": u"ㅃ",
    "qt": u"ㅄ",
    "t": u"ㅅ",
    "T": u"ㅆ",
    "d": u"ㅇ",
    "w": u"ㅈ",
    "W": u"ㅉ",
    "c": u"ㅊ",
    "z": u"ㅋ",
    "x": u"ㅌ",
    "v": u"ㅍ",
    "g": u"ㅎ",
    "k": u"ㅏ",
    "o": u"ㅐ",
    "i": u"ㅑ",
    "O": u"ㅒ",
    "j": u"ㅓ",
    "p": u"ㅔ",
    "u": u"ㅕ",
    "P": u"ㅖ",
    "h": u"ㅗ",
    "hk": u"ㅘ",
    "ho": u"ㅙ",
    "hl": u"ㅚ",
    "y": u"ㅛ",
    "n": u"ㅜ",
    "nj": u"ㅝ",
    "np": u"ㅞ",
    "nl": u"ㅟ",
    "b": u"ㅠ",
    "m": u"ㅡ",
    "l": u"ㅣ",
    "ml": u"ㅢ"}


class Converter:
    def __init__(self):
        self.finished = False

    def NumbersToUniNumber(self, cho, jung, jong):
        return 44032 + (cho * 21 + jung) * 28 + jong
    def KeyboardStrToUni(self, keystr):
        uni = ""
        finished = False
        finishedIdx = -1
        if len(keystr) == 1:
            # cho1 - singles
            # jung1 - singles
            # jong1 - singles
            if keystr in singlesStr2Uni.keys(): # ㄱ,ㄴ,ㄷ,ㅏ,...
                uni = singlesStr2Uni[keystr]
                finished = False
                finishedIdx = -1
                return uni, finished, finishedIdx, uni
            else:
                print keystr
                assert False



        elif len(keystr) == 2:
            # cho1 jung1
            # singles, singles
            if keystr in singlesStr2Uni.keys(): # ㅟ,ㄺ,... ...
                uni = singlesStr2Uni[keystr]
                finished = False # not finished here because it can be backspaced.
                finishedIdx = 1 # well value doesn't matter but put correct one.
                return uni, finished, finishedIdx, uni

            else: # not in the singles list
                if keystr[0] in chosung: # ㄱ
                    cho = chosung.index(keystr[0])
                    if keystr[1] in jungsung: # 가
                        jung = jungsung.index(keystr[1])
                        uni = unichr(self.NumbersToUniNumber(cho, jung, 0))
                        finished = False
                        finishedIdx = 1
                        return uni, finished, finishedIdx, uni

                    elif keystr[1] in singlesStr2Uni: #ㄱㄱ
                        # jungsung not in the list but in the singles
                        # means first one also is considered as a single
                        uni = singlesStr2Uni[keystr[0]] + singlesStr2Uni[keystr[1]]
                        finishedUni = singlesStr2Uni[keystr[0]]
                        finished = True
                        finishedIdx = 0
                        return uni, finished, finishedIdx, finishedUni
                    else: # not in nothing
                        assert False
                elif keystr[0] in jungsung: # ㅏㅏ, ㅏㄱ
                    if keystr[1] in singlesStr2Uni:
                        uni = singlesStr2Uni[keystr[0]] + singlesStr2Uni[keystr[1]]
                        finishedUni = singlesStr2Uni[keystr[0]]
                        finished = True
                        finishedIdx = 0
                        return uni, finished, finishedIdx, finishedUni
                    else: assert False

                    
                else: # not in the chosung list
                    assert False



        elif len(keystr) == 3: # if its length is more than 3
            # cho1 jung1 jong1
            # jung2 singles1
            # cho1 jung1 singles1
            if keystr[0:2] in singlesStr2Uni.keys():
                if keystr[2] in singlesStr2Uni.keys(): # not backspaced on stage length 2
                    # means it's: ㅟㄴ
                    uni = singlesStr2Uni[keystr[0:2]] + singlesStr2Uni[keystr[2]]
                    finished = True
                    finishedIdx = 1
                    finishedUni = singlesStr2Uni[keystr[0:2]]
                    return uni, finished, finishedIdx, finishedUni
                else:
                    assert False

            elif keystr[0] in chosung: # ㄱ
                cho = chosung.index(keystr[0])
                if keystr[1:3] in jungsung: # 귀
                    jung = jungsung.index(keystr[1:3])
                    uni = unichr(self.NumbersToUniNumber(cho, jung, 0))
                    finished = False
                    finishedIdx = 2
                    return uni, finished, finishedIdx, uni

                elif keystr[1] in jungsung: # 가
                    jung = jungsung.index(keystr[1])
                    if keystr[2] in jongsung: # 긴
                        jong = jongsung.index(keystr[2])
                        uni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                        finished = False
                        finishedIdx = 2
                        return uni, finished, finishedIdx, uni
                    elif keystr[2] in singlesStr2Uni: # 기ㅃ
                        uni = unichr(self.NumbersToUniNumber(cho, jung, 0)) + singlesStr2Uni[keystr[2]]
                        finished = True
                        finishedIdx = 1
                        finishedUni = unichr(self.NumbersToUniNumber(cho, jung, 0))
                        return uni, finished, finishedIdx, finishedUni
                    else: assert False

                elif keystr[1] in chosung:
                    #if keystr[2] in jungsung: # ㄱ가
                    # wait. not possible. it will be stopped on stage length==2
                    # rr -> ㄱㄱ means finished = True, finishedIdx = 0.
                    assert False
                else:
                    assert False
            else:
                assert False



        elif len(keystr) == 4:
            # 각ㅇ : cho1 jung1 jong1 extra1
            # 가가(각 + ㅏ) finishes on idx 1.: cho1 jung1 extracho1#2 extrajung1#2
            # 관 : cho1 jung2 jong1
            # 과ㅃ : cho1 jung2 extra1
            # 갉: cho1 jung1 jong2
            if keystr[0] in chosung: # cho1
                cho = chosung.index(keystr[0])
                if keystr[1:3] in jungsung: # jung2
                    jung = jungsung.index(keystr[1:3])
                    if keystr[3] in jongsung: # jong1
                        jong = jongsung.index(keystr[3])
                        uni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                        finished = False
                        finishedIdx = 3
                        return uni, finished, finishedIdx, uni
                    elif keystr[3] in singlesStr2Uni: # extra1
                        uni = unichr(self.NumbersToUniNumber(cho, jung, 0)) + singlesStr2Uni[keystr[3]]
                        finished = True
                        finishedIdx = 2
                        finishedUni = unichr(self.NumbersToUniNumber(cho, jung, 0))
                        return uni, finished, finishedIdx, finishedUni
                    else:
                        assert False

                elif keystr[1] in jungsung: # jung1
                    jung = jungsung.index(keystr[1])

                    def Cho1Jung1Jong1Extra1(keystr):
                        if keystr[2] in jongsung: # jong1
                            jong = jongsung.index(keystr[2])
                            if keystr[3] in singlesStr2Uni: # extra1
                                uni = unichr(self.NumbersToUniNumber(cho, jung, jong)) + \
                                        singlesStr2Uni[keystr[3]]
                                finished = True
                                finishedIdx = 2
                                finishedUni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                                return uni, finished, finishedIdx, finishedUni
                            else:
                                assert False
                        else: assert False

                    if keystr[2:4] in jongsung:
                        jong = jongsung.index(keystr[2:4])
                        uni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                        finished = False
                        finishedIdx = 3
                        finishedUni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                        return uni, finished, finishedIdx, finishedUni

                    elif keystr[2] in chosung: # cho1 jung1 extracho1 extrajung1
                        # it comes first because if we test Cho1Jung1Jong1Extra1 first,
                        # it will return 각ㅏ for rkrk which has to be rendered as
                        # 가가.
                        cho2 = chosung.index(keystr[2])
                        if keystr[3] in jungsung:
                            jung2 = jungsung.index(keystr[3])
                            uni = unichr(self.NumbersToUniNumber(cho, jung, 0)) + \
                                unichr(self.NumbersToUniNumber(cho2, jung2, 0))
                            finished = True
                            finishedIdx = 1
                            finishedUni = unichr(self.NumbersToUniNumber(cho, jung, 0))
                            return uni, finished, finishedIdx, finishedUni

                        else: # could be jong1, chosung and jongsung has same chars.
                            return Cho1Jung1Jong1Extra1(keystr)

                    elif keystr[2] in jongsung: # jong1
                        return Cho1Jung1Jong1Extra1(keystr)

                    else:
                        assert False
                else:
                    assert False
            else:
                assert False


        elif len(keystr) == 5:
            # 관ㄱ cho1 jung2 jong1 extra(single)1
            # 과나 cho1 jung2 extracho1 extrajung1
            # 괅 cho1 jung2 jong2
            # 갉ㄱ cho1 jung1 jong2 extra1
            # 갈가 cho1 jung1 jong1 extracho1 extrajung1

            if keystr[0] in chosung:
                cho = chosung.index(keystr[0])
                if keystr[1:3] in jungsung:
                    jung = jungsung.index(keystr[1:3])

                    def Cho1Jung2Jong1Extra1(keystr):
                        if keystr[3] in jongsung:
                            jong = jongsung.index(keystr[3])
                            if keystr[4] in singlesStr2Uni:
                                uni = unichr(self.NumbersToUniNumber(cho, jung, jong)) + \
                                        singlesStr2Uni[keystr[4]]
                                finished = True
                                finishedIdx = 3
                                finishedUni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                                return uni, finished, finishedIdx, finishedUni
                            else: assert False
                        else: assert False

                    if keystr[3:5] in jongsung: # ㄱ ㅘ ㄺ
                        jong = jongsung.index(keystr[3:5])
                        uni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                        finished = False
                        finishedIdx = 4
                        return uni, finished, finishedIdx, uni

                    elif keystr[3] in chosung: # possible 과나 or same chosung in jongsung == 관ㄱ
                        cho2 = chosung.index(keystr[3])
                        if keystr[4] in jungsung:
                            jung2 = jungsung.index(keystr[4])
                            uni = unichr(self.NumbersToUniNumber(cho, jung, 0)) + \
                                    unichr(self.NumbersToUniNumber(cho2, jung2, 0))
                            finished = True
                            finishedIdx = 2
                            finishedUni = unichr(self.NumbersToUniNumber(cho, jung, 0))
                            return uni, finished, finishedIdx, finishedUni
                        else:
                            return Cho1Jung2Jong1Extra1(keystr)

                    elif keystr[3] in jongsung:
                        return Cho1Jung2Jong1Extra1(keystr)

                    else: assert False
                elif keystr[1] in jungsung:
                    jung = jungsung.index(keystr[1])
                    if keystr[2] in jongsung:
                        jong = jongsung.index(keystr[2])
                        if keystr[3] in chosung and keystr[4] in jungsung:
                            cho2 = chosung.index(keystr[3])
                            jung2 = jungsung.index(keystr[4])
                            uni = unichr(self.NumbersToUniNumber(cho, jung, jong)) + \
                                    unichr(self.NumbersToUniNumber(cho2, jung2, 0))
                            finished = True
                            finishedIdx = 2
                            finishedUni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                            return uni, finished, finishedIdx, finishedUni
                        elif keystr[2:4] in jongsung:
                            jong = jongsung.index(keystr[2:4])
                            if keystr[4] in singlesStr2Uni:
                                uni = unichr(self.NumbersToUniNumber(cho, jung, jong)) + \
                                        singlesStr2Uni[keystr[4]]
                                finished = True
                                finishedIdx = 3
                                finishedUni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                                return uni, finished, finishedIdx, finishedUni
                            else: assert False
                        else: assert False


                    else: assert False
                else: assert False
            else: assert False


        elif len(keystr) == 6: # always check one more before you finish
            # 괅ㄱ cho1 jung2 jong2 extra1
            # 괄가 cho1 jung2 jong1 extracho1 extrajung1

            if keystr[0] in chosung:
                cho = chosung.index(keystr[0])
                if keystr[1:3] in jungsung:
                    jung = jungsung.index(keystr[1:3])
                    def Cho1Jung2Jong2Extra1(keystr):
                        if keystr[3:5] in jongsung:
                            jong = jongsung.index(keystr[3:5])
                            if keystr[5] in singlesStr2Uni:
                                uni = unichr(self.NumbersToUniNumber(cho, jung, jong)) + \
                                        singlesStr2Uni[keystr[5]]
                                finished = True
                                finishedIdx = 4
                                finishedUni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                                return uni, finished, finishedIdx, finishedUni
                            else: assert False
                        else: assert False

                    if keystr[3] in jongsung:
                        jong = jongsung.index(keystr[3])
                        if keystr[4] in chosung and keystr[5] in jungsung:
                            cho2 = chosung.index(keystr[4])
                            jung2 = jungsung.index(keystr[5])
                            uni = unichr(self.NumbersToUniNumber(cho, jung, jong)) + \
                                    unichr(self.NumbersToUniNumber(cho2, jung2, 0))
                            finished = True
                            finishedIdx = 3
                            finishedUni = unichr(self.NumbersToUniNumber(cho, jung, jong))
                            return uni, finished, finishedIdx, finishedUni
                        else:
                            return Cho1Jung2Jong2Extra1(keystr)

                    elif keystr[3:5] in jongsung:
                        return Cho1Jung2Jong2Extra1(keystr)

                    else: assert False
                else: assert False
            else: assert False
        else: assert False
        


class HangulComposer:
    def __init__(self):
        self.converter = Converter()
        self.buffer = ""

    def feed(self, key):
        if key not in chosung+jungsung+jongsung+singlesStr2Uni.keys():
            key = key.lower()
        self.buffer += key
        assert len(self.buffer) <= 6
        try:
            uni, finished, finishedIdx, finishedUni = self.converter.KeyboardStrToUni(self.buffer)
        except:
            print self.buffer
            raise
        if finished:
            self.buffer = self.buffer[finishedIdx+1:]
        return uni, finished, finishedUni
    def backspace(self):
        if self.buffer:
            self.buffer = self.buffer[:-1]
            if not self.buffer:
                return None
            else:
                uni, finished, finishedIdx, finishedUni = self.converter.KeyboardStrToUni(self.buffer)
                return uni, finished, finishedUni
        else:
            return None

    def get(self):
        if self.buffer:
            uni, finished, finishedIdx, finishedUni = self.converter.KeyboardStrToUni(self.buffer)
            return uni, finished, finishedUni
        else:
            assert False

    def iscomposing(self):
        if self.buffer:
            return True
        else:
            return False

    def test(self, text):
        result = []
        for c in text:
            uni, finished, finishedUni = self.feed(c)
            if finished:
                result.append(finishedUni)
        if not finished:
            result.append(uni)
        return ''.join(result)
    def finish(self):
        self.buffer = ''

if __name__ == '__main__':
    def NumbersToUniNumber(cho, jung, jong):
        return 44032 + (cho * 21 + jung) * 28 + jong
    hangulComposer = HangulComposer()
    for jong in jongsung:
        for jung in jungsung:
            for cho in chosung:
                if jong:
                    cur = cho+jung+jong
                else:
                    cur = cho+jung

                expected = unichr(NumbersToUniNumber(chosung.index(cho),
                        jungsung.index(jung),jongsung.index(jong)))
                assert hangulComposer.test(cur) == expected
                hangulComposer.finish()


