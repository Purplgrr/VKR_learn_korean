from dataclasses import dataclass
from typing import Any
from abc import ABC, abstractmethod
from konlpy.tag import Komoran, Okt
from kospellpy import spell_init
from functools import reduce
import re
# from flask import session

class TaskException(Exception):
    def __init__(self, text):
        super().__init__(text)

error_word_part_description = {
    'NA': 'в существительном',
    'NP': 'в местоимении',
    'NNG': 'в нарицательном существительном',
    'NNP': 'в собственном существительном',
    'NNB': 'в зависимом существительном',
    'NR': 'в числительном',
    'VV': 'в глаголе',
    'VA': 'в прилагательном',
    'VX': 'в вспомогательном глаголе',
    'VCP': 'в глаголе-"утверждения"',
    'VCN': 'в глаголе-"отрицания"',
    'MA': 'в наречии',
    'MAG': 'в наречии',
    'MAJ': 'в наречии',
    'IC': 'в междометии',
    'XPN': 'в префиксе существительного',
    'XSA': 'в постфиксе прилагательного',
    'XSN': 'в постфиксе существительного',
    'XSV': 'в постфиксе глагола',
    'XR': 'в корне',
    'EP': 'в окончании корня',
    'EF': 'в финальном окончании',
    'EC': 'в соединительном окончании',
    'JX': 'в суффиксе, определяющем "основное" существительное в предложении',
    'JC': 'в соединительном предлоге',
    'JKS': 'в JKS',
    'JKO': 'в JKO',
    'JKC': 'в JKC',
    'JKB': 'в JKB',
    'JKV': 'в JKV',
    'JKQ': 'в JKQ',
    'ETN': 'в окончании корня', # Надо поправить формулировку
    'ETM': 'в окончании корня', # Надо поправить формулировку
}

# link_dict = {
#     'NA': session.get('vocabulary_id', ''),
#     'NP': session.get('vocabulary_id', ''),
#     'NNG': session.get('vocabulary_id', ''),
#     'NNP': session.get('vocabulary_id', ''),
#     'NNB': session.get('vocabulary_id', ''),
#     'NR': session.get('vocabulary_id', ''),
#     'VV': session.get('vocabulary_id', ''),
#     'VA': session.get('vocabulary_id', ''),
#     'VX': session.get('vocabulary_id', ''),
#     'VCP': session.get('vocabulary_id', ''),
#     'VCN': session.get('vocabulary_id', ''),
#     'MA': session.get('vocabulary_id', ''),
#     'MAG': session.get('vocabulary_id', ''),
#     'MAJ': session.get('vocabulary_id', ''),
#     'IC': session.get('vocabulary_id', ''),
#     'XPN': session.get('theory_id', ''),
#     'XSA': session.get('theory_id', ''),
#     'XSN': session.get('theory_id', ''),
#     'XSV': session.get('theory_id', ''),
#     'XR': session.get('theory_id', ''),
#     'EP': session.get('theory_id', ''),
#     'EF': session.get('theory_id', ''),
#     'EC': session.get('theory_id', ''),
#     'JX': session.get('theory_id', ''),
#     'JC': session.get('theory_id', ''),
#     'JKS': session.get('theory_id', ''),
#     'JKO': session.get('theory_id', ''),
#     'JKC': session.get('theory_id', ''),
#     'JKB': session.get('theory_id', ''),
#     'JKV': session.get('theory_id', ''),
#     'JKQ': session.get('theory_id', ''),
#     'ETN': session.get('theory_id', ''),
#     'ETM': session.get('theory_id', '')
# }

INDEPENDENT_PARTS = {
    'NNG', 'NNP', 'NP', 'NR', 'NNB',
    'NF', 'NV', 'NA',
    'VV', 'VA', 'VX', 'VCP', 'VCN',
    'MA', 'MM', 'MAG', 'MAJ',
    'IC',
    'SF', 'SP', 'SS', 'SE', 'SO', 'SL', 'SH', 'SW'
}

initials = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
vowels = "ᅡᅢᅣᅤᅥᅦᅧᅨᅩᅪᅫᅬᅭᅮᅯᅰᅱᅲᅳᅴᅵ"
finals = "ᆨᆩᆪᆫᆬᆭᆮᆯᆰᆱᆲᆳᆴᆵᆶᆷᆸᆹᆺᆻᆼᆽᆾᆿᇀᇁᇂ"

convert_dict = {
    'ᆨ': 'ㄱ',
    'ᆩ': 'ㄲ',
    'ᆫ': 'ㄴ',
    'ᆮ': 'ㄷ',
    'ᆯ': 'ㄹ',
    'ᆷ': 'ㅁ',
    'ᆸ': 'ㅂ',
    'ᆺ': 'ㅅ',
    'ᆻ': 'ㅆ',
    'ᆼ': 'ㅇ',
    'ᆽ': 'ㅈ',
    'ᆾ': 'ㅊ',
    'ᆿ': 'ㅋ',
    'ᇀ': 'ㅌ',
    'ᇁ': 'ㅍ',
    'ᇂ': 'ㅎ',
}

verb_endings_dict = {
    'initials': {
        'present': {
            'official': {'?': '습니까', '.': '습니다'},
            'friendly': {'?': '어요', '.': '어요'}
        },
        'past': {
            'official': {'?': '었습니까', '.': '었습니다'},
            'friendly': {'?': '었어요', '.': '었어요'}
        }
    },
    'vowels': {
        'present': {
            'official': {'?': '니까', '.': '니다'},
            'friendly': {'?': '어요', '.': '어요'}
        },
        'past': {
            'official': {'?': '었습니까', '.': '었습니다'},
            'friendly': {'?': '었어요', '.': '었어요'}
        }
    }
}

noun_endings_dict = {
    'initials': {
        'present': {
            'official': {'?': '은', '.': '은'},
            'friendly': {'?': '', '.': ''},
        },
        'past': {
            'friendly': {'?': '', '.': ''},
            'official': {'?': '', '.': ''}
        }
    },
    'vowels': {
        'present': {
            'official': {'?': '는', '.': '는'},
            'friendly': {'?': '', '.': ''}
        },
        'past': {
            'friendly': {'?': '', '.': ''},
            'official': {'?': '', '.': ''}
        }
    }
}

# def get_words_with_parts(parts):
#     result = re.findall(r'\w+|,', parts)
#     result = list(map(lambda x: komoran.pos(x), result))

#     return result

    # result = []
    # index = -1

    # prefix_flag = False
    # for part in parts:
    #     # print(part, result)
    #     if part[1] in ['XPN']:
    #         index += 1
    #         prefix_flag = True
    #         result.append([part])
    #     elif part[1] in INDEPENDENT_PARTS and not prefix_flag:
    #         index += 1
    #         result.append([part])
    #     else:
    #         result[index].append(part)
    #         prefix_flag = False
    # return result

def get_character(character):
    """
    Возвращает корейский иероглиф, разложенный на начальную, гласную и конечную части.

    Args:
        character (str): Корейский иероглиф.

    Returns:
        str: Строка, состоящая из начальной, гласной и конечной частей иероглифа.
    """
    initials = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
    vowels = "ᅡᅢᅣᅤᅥᅦᅧᅨᅩᅪᅫᅬᅭᅮᅯᅰᅱᅲᅳᅴᅵ"
    finals = "ᆨᆩᆪᆫᆬᆭᆮᆯᆰᆱᆲᆳᆴᆵᆶᆷᆸᆹᆺᆻᆼᆽᆾᆿᇀᇁᇂ"

    code_point = ord(character)
    hangul_start = 44032

    if code_point < hangul_start:
        return character

    tail_index = (code_point - hangul_start) % 28 - 1
    vowel_index = ((code_point - hangul_start - tail_index) % 588) // 28
    initial_index = (code_point - hangul_start) // 588

    lead = initials[initial_index]
    vowel = vowels[vowel_index]
    tail = finals[tail_index] if tail_index >= 0 else ""

    return (lead, vowel, tail)

def compose_hangul(initial, vowel, final):
    initials = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
    vowels = "ᅡᅢᅣᅤᅥᅦᅧᅨᅩᅪᅫᅬᅭᅮᅯᅰᅱᅲᅳᅴᅵ"
    finals = "ᆨᆩᆪᆫᆬᆭᆮᆯᆰᆱᆲᆳᆴᆵᆶᆷᆸᆹᆺᆻᆼᆽᆾᆿᇀᇁᇂ"

    initial_index = initials.index(initial)
    vowel_index = vowels.index(vowel)
    if final:
        final_index = finals.index(final)
    else:
        final_index = -1

    hangul_start = 44032
    code_point = hangul_start + (initial_index * 588) + (vowel_index * 28) + (final_index + 1)

    return chr(code_point)

def get_edited_words(words, sentence_style, sentence_ending, sentence_time, ignore_noun=False):
    edited_words = []
    
    for index, word in enumerate(words):
        _word = ''
        for part in word:
            # print(part)
            if part[1] in ['VV']:#['VV', 'VA', 'VX', 'XCV']:
                symbols = list(part[0])
                chars = get_character(symbols[-1])

                # print(symbols)

                if convert_dict.get(chars[2], '/') in initials:
                    if sentence_time == 'present':
                        ending = verb_endings_dict['initials'][sentence_time][sentence_style][sentence_ending]
                    if sentence_time == 'past':
                        ending = verb_endings_dict['initials'][sentence_time][sentence_style][sentence_ending]
                elif chars[1] in vowels:
                    if sentence_time == 'present':
                        if sentence_style == 'official':
                            symbols[-1] = compose_hangul(chars[0], chars[1], 'ᆸ')
                            ending = verb_endings_dict['vowels'][sentence_time][sentence_style][sentence_ending]
                        if sentence_style == 'friendly':
                            if chars[1] in ["ᅡ", "ᅩ"]:
                                ending = '아요'
                            else:
                                ending = verb_endings_dict['vowels'][sentence_time][sentence_style][sentence_ending]
                    if sentence_time == 'past':
                        if sentence_style == 'friendly':
                            if chars[1] in ["ᅡ", "ᅩ"]:
                                ending = '았어요'
                            else:
                                ending = verb_endings_dict['vowels'][sentence_time][sentence_style][sentence_ending]
                        if sentence_style == 'official':
                            if chars[1] in ["ᅡ", "ᅩ"]:
                                ending = '았습니다'
                            else:
                                ending = verb_endings_dict['vowels'][sentence_time][sentence_style][sentence_ending]

                        
                else:
                    ending = ''
                _word += ''.join(symbols) + ending
                break
            print(part, index, not ignore_noun)
            if part[1] in ['NNP', 'NNG', 'NP'] and index == 0 and not ignore_noun:
                symbols = list(part[0])
                chars = get_character(symbols[-1])
                print(part, convert_dict.get(chars[2], '/'), chars[1] )
                if convert_dict.get(chars[2], '/') in initials:
                    if sentence_time == 'present':
                        ending = noun_endings_dict['initials'][sentence_time][sentence_style][sentence_ending]
                elif chars[1] in vowels:
                    if sentence_time == 'present':
                        ending = noun_endings_dict['vowels'][sentence_time][sentence_style][sentence_ending]
                else:
                    ending = ''
                _word += ''.join(symbols) + ending
                break
            else:
                _word += part[0]
        edited_words.append(_word)
    
    return edited_words

class PartOrderChecker:
    def __init__(self, word_with_parts):
        self.word_with_parts = word_with_parts
        self.state = None
        self.part_index = -1

    def get_next_part(self):
       self.part_index += 1

    def check(self):
        self.get_next_part()

        if self.part_index == len(self.word_with_parts):
            return
        cur_part = self.word_with_parts[self.part_index]

        if not self.state:
            self.state = cur_part[1]
            if self.state in ['EP', 'EF', 'EC', 'ETN', 'ETM', 'JX', 'JC', 'XSV', 
                            'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'XSN', 'XSA']:
                raise TaskException(f"Неверный порядок частей слова")
            self.check()

        else:
            if self.state in ['NNB', 'NNG', 'NNP']:
                cur_part = self.word_with_parts[self.part_index]
                
                if cur_part[1] in ['NNB', 'NNG', 'NNP']:
                    raise TaskException(f'''
                        Неверный порядок частей слова. 
                        Ошибка {error_word_part_description[cur_part[1]]}: {cur_part[0]}
                    ''')
                self.state = cur_part[1]
                self.check()

            elif self.state in ['XPN']:
                cur_part = self.word_with_parts[self.part_index]
                
                if cur_part[1] not in ['NNG', 'NNP']:
                    raise TaskException(f"Неверный порядок частей слова. Ошибка {error_word_part_description[self.state]}: {self.word_with_parts[self.part_index - 1]}")
                self.state = cur_part[1]
                self.check()

            elif self.state in ['NNG', 'NNP']:
                cur_part = self.word_with_parts[self.part_index]

                if cur_part[1] in ['XSV', 'XSA']:
                    raise TaskException(f"Неверный порядок частей слова. Ошибка {error_word_part_description[cur_part[1]]}: {cur_part[0]}")
                self.state = cur_part[1]
                self.check()

            elif self.state in ['MAG', 'MAJ', 'MM']:
                cur_part = self.word_with_parts[self.part_index]

                if cur_part[1] in ['EP', 'EF', 'EC', 'ETN', 'ETM', 'JX', 'JC', 'XSV', 'JKS', 
                                   'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'XSN', 'XSA']:
                    raise TaskException(f"Неверный порядок частей слова. Ошибка {error_word_part_description[self.state]}: {self.word_with_parts[self.part_index - 1]}")
                self.state = cur_part[1]
                self.check()

            elif self.state in ['JKS', 'JKC', 'JKG', 'JKO', 
                                'JKB', 'JKV', 'JKQ', 'JX', 'JC']:
                raise TaskException(f"Неверный порядок частей словa")
            else:
                self.state = cur_part[1]
                self.check()

class WordOrderChecker:
    def __init__(self, words):
        self.words = words
        self.state = None
        self.word_index = -1
        self.is_verb_reached = False

    def get_next_word(self):
        self.word_index += 1

    def check(self):
        self.get_next_word()

        if self.word_index == len(self.words):
            return
        cur_word = self.words[self.word_index]
        if not self.state:
            self.state = cur_word[1]
            # if len(self.words) != 1 and self.state in ['Verb']:
            #     raise TaskException(f"Неверный порядок слов в предложении")
            self.check()
        else:
            if self.state in ['Adjective']:
                cur_word = self.words[self.word_index]

                if self.words[self.word_index - 1] in ['네', '아니요'] and cur_word[0] != ',':
                    raise TaskException(f"Пропущена запятая")

                if cur_word[1] in ['Josa']:
                    raise TaskException(f"Неверное расположение суффикса {cur_word[0]}")
                self.state = cur_word[1]
                self.check()

            elif self.state in ['Verb'] or self.is_verb_reached:
                self.is_verb_reached = True
                cur_word = self.words[self.word_index]

                if cur_word[1] in ['Noun', 'Josa']:
                    raise TaskException(f"Неверный порядок слов. После глагола не может следовать {'суффикс' if cur_word[1] == 'Josa' else 'существительное'} {cur_word[0]}")
                self.state = cur_word[1]
                self.check()

            elif self.state in ['Punctuation']:
                cur_word = self.words[self.word_index]
                if cur_word[1] in ['Punctuation', 'Josa']:
                    raise TaskException(f"После знака пунктуации не может быть {'еще одного знака пунктуации' if cur_word[1] == 'Punctuation' else 'суффикса'}")
            else:
                self.state = cur_word[1]
                self.check()
