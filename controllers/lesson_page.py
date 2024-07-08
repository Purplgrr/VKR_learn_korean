from app import app, DATABASE_NAME
from flask import render_template, request, session, flash, redirect, url_for
from utils import get_db_connection, pictures, complete_sentence_picture
from models.lesson_page import *
import json
# from task import *
from kospellpy import spell_init
from konlpy.tag import Komoran, Okt, Kkma
from itertools import chain
from task import get_edited_words, PartOrderChecker, WordOrderChecker, TaskException, error_word_part_description
import re

komoran = Komoran()
okt = Okt()
kkma = Kkma()
spell_checker = spell_init()


def split_text_into_sentences(text):
    sentences = re.split(r'[.!?]+|\?', text)
    return [s.strip() + p for s, p in zip(sentences, re.findall(r'[.!?]+|\?', text))]

def get_words_with_parts(parts):
    result = re.findall(r'\w+|[,.!?]', parts)
    result = list(map(lambda x: komoran.pos(x), result))

    return result

def checkNounsEndings(nouns):
    temp = list(map(lambda item: komoran.pos(item), nouns))
    result = list(map(lambda item: len(item) > 1, temp))

    if any(result):
        raise TaskException("Обратите внимание на написанные вами существительные. Не указано окончание")


@app.route('/lesson_page/<int:lesson_id>', methods=['GET', 'POST'])
def lesson_page(lesson_id):
    conn = get_db_connection(DATABASE_NAME)
    
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = url_for('lessons')
        return redirect(url_for('login_page'))
    #########################

    page_title = get_page_title(conn, lesson_id)
    full_lesson_description = get_lesson_description(conn, lesson_id)

    voc_tasks_in_menu = get_voc_tasks_in_menu(conn, lesson_id).to_dict('records')
    theory_tasks_in_menu = get_theory_tasks_in_menu(conn, lesson_id).to_dict('records')
    dialog_task_in_menu = get_dialogue_tasks_in_menu(conn, lesson_id).to_dict('records')
    complete_sentence_task_in_menu = get_complete_sentence_tasks_in_menu(conn, lesson_id).to_dict('records')
    missing_word_task_in_menu = get_missing_word_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_in_menu = get_complete_dialog_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_with_words_in_menu = get_complete_dialog_task_with_words_in_menu(conn, lesson_id).to_dict('records')
    writing_exercise_in_menu = get_writing_exercise_in_menu(conn, lesson_id).to_dict('records')

    lesson_user_score = tuple(get_lesson_user_score(conn, session['user_id'], lesson_id)['lesson_user_score'])
    lesson_max_score = tuple(get_lesson_max_score(conn, lesson_id)['lesson_max_score'])

    session['theory_id'] = f"/task_theory/{lesson_id}/{theory_tasks_in_menu[0]['task_theory_id']}"

    html = render_template(
        'lesson_page.html',
        voc_tasks_in_menu=voc_tasks_in_menu,
        theory_tasks_in_menu=theory_tasks_in_menu,
        dialog_task_in_menu=dialog_task_in_menu,
        page_title=page_title,
        lesson_id=lesson_id,
        full_lesson_description=full_lesson_description,
        lesson_user_score=lesson_user_score[0] if lesson_user_score else 0,
        lesson_max_score=lesson_max_score[0] if lesson_max_score else 0,
        complete_sentence_task_in_menu=complete_sentence_task_in_menu,
        missing_word_task_in_menu=missing_word_task_in_menu,
        complete_dialog_task_in_menu=complete_dialog_task_in_menu,
        complete_dialog_task_with_words_in_menu=complete_dialog_task_with_words_in_menu,
        writing_exercise_in_menu=writing_exercise_in_menu,
    )
    
    return html


@app.route('/task_writing_exercise/<int:lesson_id>/<int:task_writing_exercise_id>', methods=['GET', 'POST'])
def task_writing_exercise(lesson_id, task_writing_exercise_id):
    conn = get_db_connection(DATABASE_NAME)
    
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = url_for('lessons')
        return redirect(url_for('login_page'))
    #########################

    lesson_max_score = tuple(get_lesson_max_score(conn, lesson_id)['lesson_max_score'])

    page_title = get_page_title(conn, lesson_id)
    short_lesson_description = get_lesson_short_description(conn, lesson_id)

    voc_tasks_in_menu = get_voc_tasks_in_menu(conn, lesson_id).to_dict('records')
    theory_tasks_in_menu = get_theory_tasks_in_menu(conn, lesson_id).to_dict('records')
    dialog_task_in_menu = get_dialogue_tasks_in_menu(conn, lesson_id).to_dict('records')
    complete_sentence_task_in_menu = get_complete_sentence_tasks_in_menu(conn, lesson_id).to_dict('records')
    missing_word_task_in_menu = get_missing_word_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_in_menu = get_complete_dialog_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_with_words_in_menu = get_complete_dialog_task_with_words_in_menu(conn, lesson_id).to_dict('records')
    writing_exercise_in_menu = get_writing_exercise_in_menu(conn, lesson_id).to_dict('records')

    writing_exercise = get_task_writing_exercise(conn, task_writing_exercise_id).to_dict('records')[0]
    
    task_description = writing_exercise['task_description']
    max_task_score = writing_exercise['max_task_score']
    style = writing_exercise['style']
    time = writing_exercise['time']
    theme = writing_exercise['theme']
    sentence_count = writing_exercise['sentence_count']
    print(time, '/', style)

    user_answer = ''
    right_sentences = [0 for _ in range(sentence_count)]
    if request.method == 'POST':
        if 'check' in request.form:
            user_answer = request.values.get('text', '')
            sentences = split_text_into_sentences(user_answer)
            
            is_correct = True
            correct_count = 0

            # print(sentences)
            if len(sentences) != sentence_count:
                flash(f"Должно быть {sentence_count} предложения! Проверьте пропущены ли знак пунктуации!")
                is_correct = False
            else:
                for sentence_index, sentence in enumerate(sentences):
                    ending = '?' if '?' in sentence else '.'

                    norm_words = []
                    noun_flag = False

                    for item in okt.pos(sentence, norm=True):
                        if item[1] in ['Adjective', 'Punctuation', 'Verb', 'Noun']:
                            norm_words.append(item[0])
                        else:
                            if item[1] in ['Noun']:
                                norm_words.append(item[0])
                                noun_flag = True
                            if item[1] in ['Josa'] and noun_flag:
                                noun_flag = False
                                norm_words[-1] += item[0]
                    # print('norm', norm_words)
                    words = get_words_with_parts(' '.join(norm_words))
                    edited_words = get_edited_words(words, style, ending, time, True)

                    print(edited_words)
                    # print('111', get_edited_words(get_words_with_parts(' '.join(user_answer)), style, ending, time, True))
                    
                    final_edited_words = []
                    for word in edited_words:
                        temp_word = word
                        try:
                            temp_word = spell_checker(word)
                        except:
                            pass
                        final_edited_words.append(temp_word)

                    try:
                        word_order = WordOrderChecker(okt.pos(sentence))
                        word_order.check()

                        for word in get_words_with_parts(sentence):
                            part_order = PartOrderChecker(word)
                            part_order.check()
                        checkNounsEndings(komoran.nouns(sentence))

                        for index, item in enumerate(final_edited_words):
                            # print('Art', re.sub(r'[.\s?!]', '', item), sentence)
                            if re.sub(r'[.\s?!]', '', item) not in sentence:
                                is_correct = False
                                flash(f'''
                                        Проверьте правильность написания суффикса/окончания слова {norm_words[index]}.
                                ''')
                            
                    except Exception as exc:
                        flash(exc) 
                        is_correct = False

                    else:
                        try:
                            spell_checked_answer = spell_checker(sentence)
                        except:
                            spell_checked_answer = sentence
                        else:
                            # print('CCC', spell_checked_answer.strip(), sentence.strip())
                            if spell_checked_answer.strip() != sentence.strip():
                                
                                spell_checked_answer_words = get_words_with_parts(spell_checked_answer)#komoran.pos(spell_checked_answer))
                                user_answer_words = get_words_with_parts(sentence)#komoran.pos(user_answer))
                                is_correct = True
                                for index, item in enumerate(user_answer_words):
                                    if spell_checked_answer_words[index] != item:
                                        error = item
                                        possible_variant = spell_checked_answer_words[index]
                                        

                                        flash(f'''
                                            Ошибка {error_word_part_description[error[0][1]]} '{''.join(list(map(lambda x: x[0], error)))}'. Вероятно вы имели в виду: {''.join(list(map(lambda x: x[0], possible_variant)))}
                                        ''')
                                        is_correct = False
                                        break
                                if is_correct:
                                    correct_count += 1
                                    right_sentences[sentence_index] = 1
                            
                    
                    if is_correct:
                        correct_count += 1
                        right_sentences[sentence_index] = 1
            
            final_score = int((correct_count / sentence_count) * max_task_score)
            update_task_writing_exercise_result(conn, session['user_id'], task_writing_exercise_id, final_score)


    lesson_user_score = tuple(get_lesson_user_score(conn, session['user_id'], lesson_id)['lesson_user_score'])
    my_task_score = int(get_task_writing_exercise_score(conn, task_writing_exercise_id, session['user_id']))

    lesson_user_score=lesson_user_score[0] if lesson_user_score else 0
    lesson_max_score=lesson_max_score[0] if lesson_max_score else 0

    if (lesson_max_score // 2 <= lesson_user_score):
        user_lesson_id = update_user_lesson(conn, lesson_id, session['user_id'])
        session['lesson_id'] = user_lesson_id
    # print([text for index, text in enumerate(split_text_into_sentences(user_answer)) if index in right_sentences])
    html = render_template(
        'task_writing_exercise.html',
        voc_tasks_in_menu=voc_tasks_in_menu,
        page_title=page_title,
        theory_tasks_in_menu=theory_tasks_in_menu,
        short_lesson_description=short_lesson_description,
        task_description=task_description,
        max_task_score=max_task_score,
        my_task_score=my_task_score,
        lesson_user_score=lesson_user_score,
        lesson_max_score=lesson_max_score,
        dialog_task_in_menu=dialog_task_in_menu,
        complete_sentence_task_in_menu=complete_sentence_task_in_menu,
        missing_word_task_in_menu=missing_word_task_in_menu,
        complete_dialog_task_in_menu=complete_dialog_task_in_menu,
        dumps=json.dumps,
        complete_dialog_task_with_words_in_menu=complete_dialog_task_with_words_in_menu,
        theme=theme,
        sentence_count=sentence_count,
        user_answer=user_answer,
        # right_sentences=[text for index, text in split_text_into_sentences(user_answer) if index in right_sentences],
        writing_exercise_in_menu=writing_exercise_in_menu,
    )
    
    return html


@app.route('/task_complete_dialog_with_words/<int:lesson_id>/<int:task_complete_dialog_with_words_id>', methods=['GET', 'POST'])
def task_complete_dialog_with_words(lesson_id, task_complete_dialog_with_words_id):
    conn = get_db_connection(DATABASE_NAME)
    
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = url_for('lessons')
        return redirect(url_for('login_page'))
    #########################

    lesson_max_score = tuple(get_lesson_max_score(conn, lesson_id)['lesson_max_score'])

    page_title = get_page_title(conn, lesson_id)
    short_lesson_description = get_lesson_short_description(conn, lesson_id)

    voc_tasks_in_menu = get_voc_tasks_in_menu(conn, lesson_id).to_dict('records')
    theory_tasks_in_menu = get_theory_tasks_in_menu(conn, lesson_id).to_dict('records')
    dialog_task_in_menu = get_dialogue_tasks_in_menu(conn, lesson_id).to_dict('records')
    complete_sentence_task_in_menu = get_complete_sentence_tasks_in_menu(conn, lesson_id).to_dict('records')
    missing_word_task_in_menu = get_missing_word_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_in_menu = get_complete_dialog_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_with_words_in_menu = get_complete_dialog_task_with_words_in_menu(conn, lesson_id).to_dict('records')
    writing_exercise_in_menu = get_writing_exercise_in_menu(conn, lesson_id).to_dict('records')

    complete_dialog_task_with_words = get_task_complete_dialog_with_words_dialog(conn, task_complete_dialog_with_words_id).to_dict('records')

    task_data = get_task_complete_dialog_with_words_data(conn, task_complete_dialog_with_words_id)
    max_task_score = task_data['max_task_score']
    task_description = task_data['task_description']

    data_dict = {str(item['complete_dialog_with_words_id']): '' for item in complete_dialog_task_with_words}
    correct_answers = {str(item['complete_dialog_with_words_id']): '' for item in complete_dialog_task_with_words}

    if request.method == 'POST':
        data_dict = json.loads(request.values.get('data_dict'))
        
        if 'check' in request.form:
            for row_index, key in enumerate(data_dict.keys()):
                user_answer = request.values.get(f'{key}', '')
                data_dict[f'{key}'] = user_answer

                dialog_data = list(filter(
                        lambda item: item['complete_dialog_with_words_id'] == int(key),
                        complete_dialog_task_with_words))[0]
                
                nessassary_nouns = dialog_data['nessassary_nouns'].replace(';', ' ')
                nessassary_verbs = dialog_data['nessassary_verbs'].replace(';', ' ')
                
                sentence_style = dialog_data['style']
                sentence_time = dialog_data['time']
                sentence_ending = '.'

                nouns = get_words_with_parts(nessassary_nouns)#(komoran.pos(nessassary_nouns))
                verbs = get_words_with_parts(nessassary_verbs)#(komoran.pos(nessassary_verbs))

                correct_filled_nouns = get_edited_words(nouns, sentence_style, sentence_ending, sentence_time)
                correct_filled_verbs = get_edited_words(verbs, sentence_style, sentence_ending, sentence_time)
                # print(correct_filled_nouns, correct_filled_verbs)


                final_correct_filled_nouns = []
                for noun in correct_filled_nouns:
                    temp_noun = noun
                    try:
                        temp_noun = spell_checker(noun)
                    except:
                        pass
                    final_correct_filled_nouns.append(temp_noun)

                final_correct_filled_verbs = []
                for verb in correct_filled_verbs:
                    temp_verb = verb
                    try:
                        temp_verb = spell_checker(verb)
                    except:
                        pass
                    final_correct_filled_verbs.append(temp_verb)
                print('AAA', final_correct_filled_verbs, final_correct_filled_nouns)
                word_order = WordOrderChecker(okt.pos(user_answer)) 

                for index, noun in enumerate(correct_filled_nouns):
                    # print(row_index, noun, user_answer)
                    if noun not in user_answer:
                        missing_noun = dialog_data['nessassary_nouns'].split(';')[index]
                        # print(missing_noun)
                        flash(f'{row_index + 1}. Обнаружена ошибка в вашем ответе. Убедитесь, что вы использовали предлагаемое слово {missing_noun} в правильной форме!')
                        correct_answers[str(key)] = False
                for index, verb in enumerate(correct_filled_verbs):
                    if verb not in user_answer:
                        missing_verb = dialog_data['nessassary_verb'].split(';')[index]
                        flash(f'{row_index + 1}. Обнаружена ошибка в вашем ответе. Убедитесь, что вы использовали предлагаемое слово {missing_verb} в правильной форме!')
                        correct_answers[str(key)] = False                
                if correct_answers[str(key)] or correct_answers[str(key)] == '':
                    try:
                        word_order.check()
                        for word in get_words_with_parts(user_answer):#(komoran.pos(user_answer)):
                            part_order = PartOrderChecker(word)
                            # print(word)
                            part_order.check()
                        checkNounsEndings(komoran.nouns(user_answer))
                        correct_answers[str(key)] = True
                    except Exception as exc:
                        flash(exc)
                        correct_answers[str(key)] = False
                    else:
                        try:
                            spell_checked_answer = spell_checker(user_answer)
                        except:
                            spell_checked_answer = user_answer
                        else:
                            if re.sub(r'[.\s?!]', '', spell_checked_answer) != re.sub(r'[.\s?!]', '', user_answer).strip():
                                
                                spell_checked_answer_words = get_words_with_parts(spell_checked_answer)#komoran.pos(spell_checked_answer))
                                user_answer_words = get_words_with_parts(user_answer)#komoran.pos(user_answer))
                                
                                # print(spell_checked_answer, user_answer)
                                for index, item in enumerate(user_answer_words):
                                    if spell_checked_answer_words[index] != item:
                                        error = item
                                        possible_variant = spell_checked_answer_words[index]
                                        break

                                flash(f'''
                                            Ошибка {error_word_part_description[error[0][1]]} '{''.join(list(map(lambda x: x[0], error)))}'. Вероятно вы имели в виду: {''.join(list(map(lambda x: x[0], possible_variant)))}
                                ''')
                                correct_answers[str(key)]= False
                            else:
                                correct_answers[str(key)] = True
            
            print(correct_answers)
            result = [item for item in list(correct_answers.values())]
            total_count = len(result)

            filtered_result = list(filter(lambda x: x == True, result))
            correct_count = len(filtered_result)

            user_score = int((correct_count / total_count) * max_task_score)
            update_task_complete_dialog_with_words_result(conn, session['user_id'], task_complete_dialog_with_words_id, user_score)          

    lesson_user_score = tuple(get_lesson_user_score(conn, session['user_id'], lesson_id)['lesson_user_score'])
    my_task_score = int(get_task_complete_dialog_with_words_score(conn, task_complete_dialog_with_words_id, session['user_id']))

    lesson_user_score=lesson_user_score[0] if lesson_user_score else 0
    lesson_max_score=lesson_max_score[0] if lesson_max_score else 0

    if (lesson_max_score // 2 <= lesson_user_score):
        user_lesson_id = update_user_lesson(conn, lesson_id, session['user_id'])
        session['lesson_id'] = user_lesson_id
    
    html = render_template(
        'task_complete_dialog_with_words.html',
        voc_tasks_in_menu=voc_tasks_in_menu,
        page_title=page_title,
        theory_tasks_in_menu=theory_tasks_in_menu,
        short_lesson_description=short_lesson_description,
        task_description=task_description,
        max_task_score=max_task_score,
        my_task_score=my_task_score,
        lesson_user_score=lesson_user_score,
        lesson_max_score=lesson_max_score,
        dialog_task_in_menu=dialog_task_in_menu,
        complete_sentence_task_in_menu=complete_sentence_task_in_menu,
        missing_word_task_in_menu=missing_word_task_in_menu,
        complete_dialog_task_in_menu=complete_dialog_task_in_menu,
        complete_dialog_task_with_words=complete_dialog_task_with_words,
        data_dict=data_dict,
        correct_answers=correct_answers,
        dumps=json.dumps,
        enumerate=enumerate,
        complete_dialog_task_with_words_in_menu=complete_dialog_task_with_words_in_menu,
        writing_exercise_in_menu=writing_exercise_in_menu,
    )
    
    return html


@app.route('/task_complete_dialog/<int:lesson_id>/<int:task_complete_dialog_id>', methods=['GET', 'POST'])
def task_complete_dialog(lesson_id, task_complete_dialog_id):
    conn = get_db_connection(DATABASE_NAME)
    
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = url_for('lessons')
        return redirect(url_for('login_page'))
    #########################

    lesson_max_score = tuple(get_lesson_max_score(conn, lesson_id)['lesson_max_score'])

    page_title = get_page_title(conn, lesson_id)
    short_lesson_description = get_lesson_short_description(conn, lesson_id)

    voc_tasks_in_menu = get_voc_tasks_in_menu(conn, lesson_id).to_dict('records')
    theory_tasks_in_menu = get_theory_tasks_in_menu(conn, lesson_id).to_dict('records')
    dialog_task_in_menu = get_dialogue_tasks_in_menu(conn, lesson_id).to_dict('records')
    complete_sentence_task_in_menu = get_complete_sentence_tasks_in_menu(conn, lesson_id).to_dict('records')
    missing_word_task_in_menu = get_missing_word_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_in_menu = get_complete_dialog_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_with_words_in_menu = get_complete_dialog_task_with_words_in_menu(conn, lesson_id).to_dict('records')
    writing_exercise_in_menu = get_writing_exercise_in_menu(conn, lesson_id).to_dict('records')

    complete_dialog_task = get_task_complete_dialog_dialog(conn, task_complete_dialog_id).to_dict('records')

    task_data = get_task_complete_dialog_data(conn, task_complete_dialog_id)
    max_task_score = task_data['max_task_score']
    task_description = task_data['task_description']

    data_dict = {str(item['complete_dialog_id']): {'sentence_A': '', 'sentence_B': ''} for item in complete_dialog_task}
    correct_answers = {str(item['complete_dialog_id']): {'sentence_A': None, 'sentence_B': None} for item in complete_dialog_task}
    
    if request.method == 'POST':
        data_dict = json.loads(request.values.get('data_dict'))
        if 'check' in request.form:
            i = 0
            for key, value in data_dict.items():
                i += 1
                sentence_A = request.values.get(f"sentence_A_{key}")
                sentence_B = request.values.get(f"sentence_B_{key}")

                value['sentence_A'] = sentence_A
                value['sentence_B'] = sentence_B
                
                dialog_data = list(filter(
                        lambda item: item['complete_dialog_id'] == int(key),
                        complete_dialog_task))[0]
                
                nessassary_word = dialog_data['nessassary_word']
                sentence_style = dialog_data['style']
                sentence_time = dialog_data['time']

                temp = get_words_with_parts(nessassary_word)#(komoran.pos(nessassary_word))
                if f"sentence_A_{key}" in request.values:
                    sentence_ending = '?'

                    correct_filled_answer = get_edited_words(temp, sentence_style, sentence_ending, sentence_time)[0]
                    print('AA', correct_filled_answer)
                    try:
                        correct_filled_answer = spell_checker(correct_filled_answer)
                    except:
                        correct_filled_answer = correct_filled_answer

                    full_answer = dialog_data['sentence_A'].replace(";", ' ' + sentence_A)
                    word_order = WordOrderChecker(okt.pos(full_answer))
                    print(re.sub(r'[.\s?!]', '', correct_filled_answer), full_answer) 
                    if not sentence_A:
                        correct_answers[str(key)]['sentence_A'] = False
                    elif re.sub(r'[.\s?!]', '', correct_filled_answer) not in full_answer:
                        
                        flash(f'{i}A. Обнаружена ошибка в вашем ответе: "{sentence_A}". Убедитесь, что вы использовали предлагаемое слово в правильной форме!')
                        correct_answers[str(key)]['sentence_A'] = False
                    else:
                        try:
                            word_order.check()
                            for word in get_words_with_parts(full_answer):#(komoran.pos(full_answer)):
                                part_order = PartOrderChecker(word)
                                # print(word)
                                part_order.check()
                            correct_answers[str(key)]['sentence_A'] = True
                        except Exception as exc:
                            flash(exc)
                            correct_answers[str(key)]['sentence_A'] = False
                        else:
                            try:
                                spell_checked_answer = spell_checker(full_answer)
                            except:
                                spell_checked_answer = full_answer
                            else:
                                if spell_checked_answer.strip() != full_answer.strip():
                                    # flash('Ошибка в написании!')
                                    spell_checked_answer_words = get_words_with_parts(spell_checked_answer)#(komoran.pos(spell_checked_answer))
                                    user_answer_words = get_words_with_parts(full_answer)#(komoran.pos(full_answer))

                                    error = None
                                    for index, item in enumerate(user_answer_words):
                                        if spell_checked_answer_words[index] != item:
                                            error = item
                                            possible_variant = spell_checked_answer_words[index]
                                            break
                                    
                                    if error:
                                        flash(f'''
                                            {i}A. Ошибка {error_word_part_description[error[0][1]]} '{''.join(list(map(lambda x: x[0], error)))}'. Вероятно вы имели в виду: {''.join(list(map(lambda x: x[0], possible_variant)))}
                                        ''')
                                        correct_answers[str(key)]['sentence_A'] = False
                                else:
                                    try:
                                        word_order.check()
                                        for word in get_words_with_parts(komoran.pos(full_answer)):
                                            part_order = PartOrderChecker(word)
                                            part_order.check()
                                        correct_answers[str(key)]['sentence_A'] = True
                                    except Exception as exc:
                                        flash(exc)
                                        correct_answers[str(key)]['sentence_A'] = False
                                    
                if f"sentence_B_{key}" in request.values:
                    sentence_ending = '.'

                    correct_filled_answer = get_edited_words(temp, sentence_style, sentence_ending, sentence_time)[0]
                    print(correct_filled_answer)
                    try:
                        correct_filled_answer = spell_checker(correct_filled_answer)
                    except:
                        correct_filled_answer = correct_filled_answer
                        
                    full_answer = dialog_data['sentence_B'].replace(";", ' ' + sentence_B)
                    word_order = WordOrderChecker(okt.pos(full_answer)) 
                    print(re.sub(r'[.\s?!]', '', correct_filled_answer), full_answer) 
                    # print(correct_filled_answer)
                    if not sentence_B:
                        correct_answers[str(key)]['sentence_B'] = False
                    elif re.sub(r'[.\s?!]', '', correct_filled_answer) not in full_answer:
                        print(correct_filled_answer, full_answer)
                        flash(f'{i}B. Обнаружена ошибка в вашем ответе: "{sentence_B}". Убедитесь, что вы использовали предлагаемое слово в правильной форме!')
                        correct_answers[str(key)]['sentence_B'] = False
                    else:
                        try:
                            word_order.check()
                            for word in get_words_with_parts(full_answer):#(komoran.pos(full_answer)):
                                part_order = PartOrderChecker(word)
                                part_order.check()
                            correct_answers[str(key)]['sentence_B'] = True
                        except Exception as exc:
                            flash(exc)
                            correct_answers[str(key)]['sentence_B'] = False
                        else:
                            try:
                                spell_checked_answer = spell_checker(full_answer)
                            except:
                                spell_checked_answer = full_answer
                            else:
                                if spell_checked_answer.strip() != full_answer.strip():
                                    spell_checked_answer_words = get_words_with_parts(spell_checked_answer)#(komoran.pos(spell_checked_answer))
                                    user_answer_words = get_words_with_parts(full_answer)#(komoran.pos(full_answer))

                                    error = None
                                    for index, item in enumerate(user_answer_words):
                                        if spell_checked_answer_words[index] != item:
                                            error = item
                                            possible_variant = spell_checked_answer_words[index]
                                            break
                                    if error: 
                                        flash(f'''
                                            {i}B. Ошибка {error_word_part_description[error[0][1]]} '{''.join(list(map(lambda x: x[0], error)))}'. Вероятно вы имели в виду: {''.join(list(map(lambda x: x[0], possible_variant)))}
                                        ''')
                                        correct_answers[str(key)]['sentence_B'] = False
                                else:
                                    try:
                                        word_order.check()
                                        for word in get_words_with_parts(komoran.pos(full_answer)):
                                            part_order = PartOrderChecker(word)
                                            part_order.check()
                                        correct_answers[str(key)]['sentence_B'] = True
                                    except Exception as exc:
                                        flash(exc)
                                        correct_answers[str(key)]['sentence_B'] = False
        
            temp_result = [list(item.values()) for item in list(correct_answers.values())]
            result = list(chain(*temp_result))
            
            filtered_result = list(filter(lambda x: x in [True, False], result))
            total_count = len(filtered_result)

            filtered_result = list(filter(lambda x: x == True, filtered_result))
            correct_count = len(filtered_result)

            user_score = int((correct_count / total_count) * max_task_score)
            update_task_complete_dialog_result(conn, session['user_id'], task_complete_dialog_id, user_score)

    lesson_user_score = tuple(get_lesson_user_score(conn, session['user_id'], lesson_id)['lesson_user_score'])
    my_task_score = int(get_task_complete_dialog_score(conn, task_complete_dialog_id, session['user_id']))
    
    lesson_user_score=lesson_user_score[0] if lesson_user_score else 0
    lesson_max_score=lesson_max_score[0] if lesson_max_score else 0
    
    if (lesson_max_score // 2 <= lesson_user_score):
        user_lesson_id = update_user_lesson(conn, lesson_id, session['user_id'])
        session['lesson_id'] = user_lesson_id

    html = render_template(
        'task_complete_dialog.html',
        voc_tasks_in_menu=voc_tasks_in_menu,
        page_title=page_title,
        theory_tasks_in_menu=theory_tasks_in_menu,
        short_lesson_description=short_lesson_description,
        task_description=task_description,
        max_task_score=max_task_score,
        my_task_score=my_task_score,
       lesson_user_score=lesson_user_score,
        lesson_max_score=lesson_max_score,
        dialog_task_in_menu=dialog_task_in_menu,
        complete_sentence_task_in_menu=complete_sentence_task_in_menu,
        missing_word_task_in_menu=missing_word_task_in_menu,
        complete_dialog_task_in_menu=complete_dialog_task_in_menu,
        complete_dialog_task=complete_dialog_task,
        data_dict=data_dict,
        correct_answers=correct_answers,
        dumps=json.dumps,
        enumerate=enumerate,
        complete_dialog_task_with_words_in_menu=complete_dialog_task_with_words_in_menu,
        writing_exercise_in_menu=writing_exercise_in_menu,
    )
    
    return html


@app.route('/task_missing_word_exercise/<int:lesson_id>/<int:task_missing_word_exercise_id>', methods=['GET', 'POST'])
def task_missing_word_exercise(lesson_id, task_missing_word_exercise_id):
    conn = get_db_connection(DATABASE_NAME)
    
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = url_for('lessons')
        return redirect(url_for('login_page'))
    #########################

    lesson_max_score = tuple(get_lesson_max_score(conn, lesson_id)['lesson_max_score'])

    page_title = get_page_title(conn, lesson_id)
    short_lesson_description = get_lesson_short_description(conn, lesson_id)

    voc_tasks_in_menu = get_voc_tasks_in_menu(conn, lesson_id).to_dict('records')
    theory_tasks_in_menu = get_theory_tasks_in_menu(conn, lesson_id).to_dict('records')
    dialog_task_in_menu = get_dialogue_tasks_in_menu(conn, lesson_id).to_dict('records')
    complete_sentence_task_in_menu = get_complete_sentence_tasks_in_menu(conn, lesson_id).to_dict('records')
    missing_word_task_in_menu = get_missing_word_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_in_menu = get_complete_dialog_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_with_words_in_menu = get_complete_dialog_task_with_words_in_menu(conn, lesson_id).to_dict('records')
    writing_exercise_in_menu = get_writing_exercise_in_menu(conn, lesson_id).to_dict('records')

    missing_word_exercise = get_task_missing_word_exercise_voc(conn, lesson_id, task_missing_word_exercise_id).to_dict('records')
    inserted_words = {item['vocabulary_id']: '' for item in missing_word_exercise}
    right_answers = {item['vocabulary_id']: item['korean'] for item in missing_word_exercise}

    task_data = get_task_missing_word(conn, task_missing_word_exercise_id).to_dict('records')[0]
    task_description = task_data['task_description']
    
    my_task_score = get_task_missing_word_exersice_score(conn, task_missing_word_exercise_id, session['user_id'])
    max_task_score = task_data['max_task_score']

    correct_words = []
    if request.method == 'POST':
        if 'check' in request.form:
            for key in inserted_words.keys():
                user_answer = request.values.get(str(key))
                inserted_words[key] = user_answer

                if right_answers[key] == user_answer:
                    correct_words.append(key)
                
            final_task_score = round((len(correct_words) / len(missing_word_exercise)) * max_task_score)
            update_task_missing_word_exercise_result(conn, session['user_id'], task_missing_word_exercise_id, final_task_score)
            my_task_score = final_task_score


    lesson_user_score = tuple(get_lesson_user_score(conn, session['user_id'], lesson_id)['lesson_user_score'])

    lesson_user_score=lesson_user_score[0] if lesson_user_score else 0
    lesson_max_score=lesson_max_score[0] if lesson_max_score else 0

    if (lesson_max_score // 2 <= lesson_user_score):
        update_user_lesson(conn, lesson_id, session['user_id'])
    
    html = render_template(
        'task_missing_word_exercise.html',
        voc_tasks_in_menu=voc_tasks_in_menu,
        page_title=page_title,
        theory_tasks_in_menu=theory_tasks_in_menu,
        short_lesson_description=short_lesson_description,
        task_description=task_description,
        max_task_score=max_task_score,
        my_task_score=my_task_score,
        correct_words=correct_words,
        inserted_words=inserted_words,
        missing_word_exercise=missing_word_exercise,
        lesson_user_score=lesson_user_score,
        lesson_max_score=lesson_max_score,
        dialog_task_in_menu=dialog_task_in_menu,
        complete_sentence_task_in_menu=complete_sentence_task_in_menu,
        missing_word_task_in_menu=missing_word_task_in_menu,
        pictures=pictures,
        complete_dialog_task_in_menu=complete_dialog_task_in_menu,
        complete_dialog_task_with_words_in_menu=complete_dialog_task_with_words_in_menu,
        writing_exercise_in_menu=writing_exercise_in_menu,
    )
    
    return html


@app.route('/task_complete_sentence/<int:lesson_id>/<int:task_complete_sentence_id>', methods=['GET', 'POST'])
def task_complete_sentence(lesson_id, task_complete_sentence_id):
    conn = get_db_connection(DATABASE_NAME)
    
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = url_for('lessons')
        return redirect(url_for('login_page'))
    #########################

    lesson_max_score = tuple(get_lesson_max_score(conn, lesson_id)['lesson_max_score'])

    page_title = get_page_title(conn, lesson_id)
    short_lesson_description = get_lesson_short_description(conn, lesson_id)
    
    voc_tasks_in_menu = get_voc_tasks_in_menu(conn, lesson_id).to_dict('records')
    theory_tasks_in_menu = get_theory_tasks_in_menu(conn, lesson_id).to_dict('records')
    dialog_task_in_menu = get_dialogue_tasks_in_menu(conn, lesson_id).to_dict('records')
    complete_sentence_task_in_menu = get_complete_sentence_tasks_in_menu(conn, lesson_id).to_dict('records')
    missing_word_task_in_menu = get_missing_word_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_in_menu = get_complete_dialog_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_with_words_in_menu = get_complete_dialog_task_with_words_in_menu(conn, lesson_id).to_dict('records')
    writing_exercise_in_menu = get_writing_exercise_in_menu(conn, lesson_id).to_dict('records')

    complete_sentence_task = get_task_complete_sentence_exercise(conn, lesson_id, task_complete_sentence_id).to_dict('records')

    completed_sentence_exercise = [item['complete_sentence_exercise_id'] for item in complete_sentence_task]
    completed_words = ['_' for _ in complete_sentence_task]
    
    correct_completed_exercise = []
    
    task_data = get_task_complete_sentence_data(conn, task_complete_sentence_id)
    task_description = task_data['task_description']

    max_task_score = task_data['max_task_score']
    my_task_score = get_task_complete_sentence_score(conn, task_complete_sentence_id, session['user_id']) 

    if request.method == 'POST':
        if 'check_word' in request.form:
            is_correct = int(request.values.get('is_correct'))
            complete_word_id = int(request.values.get('complete_word_id'))
            completed_sentence_exercise = request.values.get('completed_sentence_exercise')
            complete_sentence_exercise_id = int(request.values.get('complete_sentence_exercise_id'))
            completed_words = request.values.get('completed_words').split(';')
            completed_sentence_exercise = list(map(int, completed_sentence_exercise.split(';')))
            completed_words[completed_sentence_exercise.index(complete_sentence_exercise_id)] = request.values.get('check_word')
        if 'check' in request.form:
            completed_sentence_exercise = request.values.get('completed_sentence_exercise')
            completed_sentence_exercise = list(map(int, completed_sentence_exercise.split(';')))

            completed_words = request.values.get('completed_words').split(';')
            for index, complete_sentence_exercise_id in enumerate(completed_sentence_exercise):
                filtered_data = list(filter(lambda item: item['complete_sentence_exercise_id'] == complete_sentence_exercise_id, complete_sentence_task))[0]
                completed_word = completed_words[index]

                exercise_words = filtered_data['words'].split(';')
                is_correct_word = filtered_data['correct_answers'].split(';')

                for word, is_correct in zip(exercise_words, is_correct_word):
                    if int(is_correct) and word == completed_word:
                        correct_completed_exercise.append(complete_sentence_exercise_id)
            
            final_task_score = int(len(correct_completed_exercise) / len(complete_sentence_task) * max_task_score)
            update_task_complete_sentence_result(conn, session['user_id'], task_complete_sentence_id, final_task_score)
            my_task_score = final_task_score
            
    # my_task_score = get_task_complete_sentence_score(conn, task_complete_sentence_id, session['user_id']) 
    lesson_user_score = tuple(get_lesson_user_score(conn, session['user_id'], lesson_id)['lesson_user_score'])

    lesson_user_score=lesson_user_score[0] if lesson_user_score else 0
    lesson_max_score=lesson_max_score[0] if lesson_max_score else 0

    if (lesson_max_score // 2 <= lesson_user_score):
        user_lesson_id = update_user_lesson(conn, lesson_id, session['user_id'])
        session['lesson_id'] = user_lesson_id
    
    task_picture = complete_sentence_picture.get(task_complete_sentence_id, '/static/images/3rd_lesson.png')
    
    html = render_template(
        'task_complete_sentence.html',
        voc_tasks_in_menu=voc_tasks_in_menu,
        page_title=page_title,
        complete_sentence_task=complete_sentence_task,
        theory_tasks_in_menu=theory_tasks_in_menu,
        short_lesson_description=short_lesson_description,
        task_description=task_description,
        max_task_score=max_task_score,
        my_task_score=my_task_score,
        completed_words=';'.join(completed_words),
        correct_completed_exercise=correct_completed_exercise,
        list=list,
        completed_sentence_exercise=';'.join(list(map(str, completed_sentence_exercise))),
        lesson_user_score=lesson_user_score,
        lesson_max_score=lesson_max_score,
        dialog_task_in_menu=dialog_task_in_menu,
        complete_sentence_task_in_menu=complete_sentence_task_in_menu,
        missing_word_task_in_menu=missing_word_task_in_menu,
        complete_dialog_task_in_menu=complete_dialog_task_in_menu,
        complete_dialog_task_with_words_in_menu=complete_dialog_task_with_words_in_menu,
        writing_exercise_in_menu=writing_exercise_in_menu,
        task_picture=task_picture,
    )
    
    return html


@app.route('/task_voc/<int:lesson_id>/<int:task_voc_id>', methods=['GET', 'POST'])
def task_voc(lesson_id, task_voc_id):
    conn = get_db_connection(DATABASE_NAME)
    
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = url_for('lessons')
        return redirect(url_for('login_page'))
    #########################

    lesson_max_score = tuple(get_lesson_max_score(conn, lesson_id)['lesson_max_score'])

    page_title = get_page_title(conn, lesson_id)
    short_lesson_description = get_lesson_short_description(conn, lesson_id)

    voc_tasks_in_menu = get_voc_tasks_in_menu(conn, lesson_id).to_dict('records')
    theory_tasks_in_menu = get_theory_tasks_in_menu(conn, lesson_id).to_dict('records')
    dialog_task_in_menu = get_dialogue_tasks_in_menu(conn, lesson_id).to_dict('records')
    complete_sentence_task_in_menu = get_complete_sentence_tasks_in_menu(conn, lesson_id).to_dict('records')
    missing_word_task_in_menu = get_missing_word_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_in_menu = get_complete_dialog_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_with_words_in_menu = get_complete_dialog_task_with_words_in_menu(conn, lesson_id).to_dict('records')
    writing_exercise_in_menu = get_writing_exercise_in_menu(conn, lesson_id).to_dict('records')

    voc_task = get_voc_task(conn, lesson_id, task_voc_id).to_dict('records')

    task_voc_data = get_task_voc(conn, task_voc_id).to_dict('records')[0]
    task_description = task_voc_data['task_description']
    max_task_score = task_voc_data['max_task_score']
    my_task_score = get_task_voc_score(conn, task_voc_id, session['user_id'])    

    if request.method == 'POST':
        if 'add_voc_fav' in request.form:
            vocabulary_id = int(request.form.get('vocabulary_id'))
            add_voc_fav(conn, session['user_id'], vocabulary_id)
        elif 'del_voc_fav' in request.form:
            vocabulary_id = int(request.form.get('vocabulary_id'))
            del_voc_fav(conn, session['user_id'], vocabulary_id)
        elif 'check' in request.form:
            update_task_voc_result(conn, session['user_id'], task_voc_id, max_task_score)  
      
    my_task_score = get_task_voc_score(conn, task_voc_id, session['user_id'])  
    max_task_score = task_voc_data['max_task_score']
    my_task_score = get_task_voc_score(conn, task_voc_id, session['user_id'])
    fav_voc = list(get_voc_fav(conn, session['user_id'])['vocabulary_id'])

    lesson_user_score = tuple(get_lesson_user_score(conn, session['user_id'], lesson_id)['lesson_user_score'])

    lesson_user_score=lesson_user_score[0] if lesson_user_score else 0
    lesson_max_score=lesson_max_score[0] if lesson_max_score else 0

    if (lesson_max_score // 2 <= lesson_user_score):
        user_lesson_id = update_user_lesson(conn, lesson_id, session['user_id'])
        session['lesson_id'] = user_lesson_id

    html = render_template(
        'task_voc.html',
        voc_tasks_in_menu=voc_tasks_in_menu,
        page_title=page_title,
        voc_task=voc_task,
        theory_tasks_in_menu=theory_tasks_in_menu,
        fav_voc=fav_voc,
        short_lesson_description=short_lesson_description,
        task_description=task_description,
        max_task_score=max_task_score,
        my_task_score=my_task_score,
        lesson_user_score=lesson_user_score,
        lesson_max_score=lesson_max_score,
        dialog_task_in_menu=dialog_task_in_menu,
        complete_sentence_task_in_menu=complete_sentence_task_in_menu,
        missing_word_task_in_menu=missing_word_task_in_menu,
        complete_dialog_task_in_menu=complete_dialog_task_in_menu,
        complete_dialog_task_with_words_in_menu=complete_dialog_task_with_words_in_menu,
        writing_exercise_in_menu=writing_exercise_in_menu,
    )
    
    return html



@app.route('/task_theory/<int:lesson_id>/<int:task_theory_id>', methods=['GET', 'POST'])
def task_theory(lesson_id, task_theory_id):
    conn = get_db_connection(DATABASE_NAME)
    
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = url_for('lessons')
        return redirect(url_for('login_page'))
    #########################

    lesson_max_score = tuple(get_lesson_max_score(conn, lesson_id)['lesson_max_score'])

    page_title = get_page_title(conn, lesson_id)
    short_lesson_description = get_lesson_short_description(conn, lesson_id)

    voc_tasks_in_menu = get_voc_tasks_in_menu(conn, lesson_id).to_dict('records')
    theory_tasks_in_menu = get_theory_tasks_in_menu(conn, lesson_id).to_dict('records')
    dialog_task_in_menu = get_dialogue_tasks_in_menu(conn, lesson_id).to_dict('records')
    complete_sentence_task_in_menu = get_complete_sentence_tasks_in_menu(conn, lesson_id).to_dict('records')
    missing_word_task_in_menu = get_missing_word_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_in_menu = get_complete_dialog_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_with_words_in_menu = get_complete_dialog_task_with_words_in_menu(conn, lesson_id).to_dict('records')
    writing_exercise_in_menu = get_writing_exercise_in_menu(conn, lesson_id).to_dict('records')

    theory_task = get_task_theory_theory(conn, lesson_id, task_theory_id).to_dict('records')
    theory_index = 0

    task_theory_data = get_task_theory(conn, task_theory_id).to_dict('records')[0]
    task_description = task_theory_data['task_description']
    max_task_score = task_theory_data['max_task_score']

    if request.method == 'POST':
        if 'next' in request.form:
            theory_index = int(request.form.get('theory_index')) + 1
        if 'previous' in request.form:
            theory_index = int(request.form.get('theory_index')) - 1
        if 'check' in request.form:
            update_task_theory_result(conn, session['user_id'], task_theory_id, max_task_score)
        if 'add_theory_fav' in request.form:
            theory_id = int(request.values.get('theory_id'))
            add_theory_fav(conn, session['user_id'], theory_id)
        if 'del_theory_fav' in request.form:
            theory_id = int(request.values.get('theory_id'))
            del_theory_fav(conn, session['user_id'], theory_id)


    my_task_score = get_task_theory_score(conn, task_theory_id, session['user_id'])
    print(my_task_score)
    lesson_user_score = tuple(get_lesson_user_score(conn, session['user_id'], lesson_id)['lesson_user_score'])
    fav_theory = get_fav_theory(conn, task_theory_id, session['user_id'])

    lesson_user_score=lesson_user_score[0] if lesson_user_score else 0
    lesson_max_score=lesson_max_score[0] if lesson_max_score else 0

    if (lesson_max_score // 2 <= lesson_user_score):
        user_lesson_id = update_user_lesson(conn, lesson_id, session['user_id'])
        session['lesson_id'] = user_lesson_id

    html = render_template(
        'task_theory.html',
        theory_tasks_in_menu=theory_tasks_in_menu,
        page_title=page_title,
        theory_task=theory_task,
        voc_tasks_in_menu=voc_tasks_in_menu,
        fav_theory=fav_theory,
        task_description=task_description,
        max_task_score=max_task_score,
        my_task_score=my_task_score,
        lesson_user_score=lesson_user_score,
        lesson_max_score=lesson_max_score,
        theory_index=theory_index,
        dialog_task_in_menu=dialog_task_in_menu,
        short_lesson_description=short_lesson_description,
        complete_sentence_task_in_menu=complete_sentence_task_in_menu,
        missing_word_task_in_menu=missing_word_task_in_menu,
        complete_dialog_task_in_menu=complete_dialog_task_in_menu,
        complete_dialog_task_with_words_in_menu=complete_dialog_task_with_words_in_menu,
        writing_exercise_in_menu=writing_exercise_in_menu,
    )
    
    return html


@app.route('/task_dialogue/<int:lesson_id>/<int:task_dia_id>', methods=['GET', 'POST'])
def task_dialogue(lesson_id, task_dia_id):
    conn = get_db_connection(DATABASE_NAME)
    
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = url_for('lessons')
        return redirect(url_for('login_page'))
    #########################

    lesson_max_score = tuple(get_lesson_max_score(conn, lesson_id)['lesson_max_score'])

    page_title = get_page_title(conn, lesson_id)
    short_lesson_description = get_lesson_short_description(conn, lesson_id)

    voc_tasks_in_menu = get_voc_tasks_in_menu(conn, lesson_id).to_dict('records')
    theory_tasks_in_menu = get_theory_tasks_in_menu(conn, lesson_id).to_dict('records')
    dialog_task_in_menu = get_dialogue_tasks_in_menu(conn, lesson_id).to_dict('records')
    complete_sentence_task_in_menu = get_complete_sentence_tasks_in_menu(conn, lesson_id).to_dict('records')
    missing_word_task_in_menu = get_missing_word_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_in_menu = get_complete_dialog_task_in_menu(conn, lesson_id).to_dict('records')
    complete_dialog_task_with_words_in_menu = get_complete_dialog_task_with_words_in_menu(conn, lesson_id).to_dict('records')
    writing_exercise_in_menu = get_writing_exercise_in_menu(conn, lesson_id).to_dict('records')

    dialogue_task = get_task_dialogue_dialogue(conn, lesson_id, task_dia_id).to_dict('records')
    dialogue_index = 0

    task_dia_data = get_task_dia(conn, task_dia_id).to_dict('records')[0]
    task_description = task_dia_data['task_description']
    max_task_score = task_dia_data['max_task_score']

    if request.method == 'POST':
        if 'next' in request.form:
            dialogue_index = int(request.form.get('dialogue_index')) + 1
        if 'previous' in request.form:
            dialogue_index = int(request.form.get('dialogue_index')) - 1
        if 'check' in request.form:
            update_task_dia_result(conn, session['user_id'], task_dia_id, max_task_score)

    my_task_score = get_task_dia_score(conn, task_dia_id, session['user_id'])

    lesson_user_score = tuple(get_lesson_user_score(conn, session['user_id'], lesson_id)['lesson_user_score'])

    lesson_user_score=lesson_user_score[0] if lesson_user_score else 0
    lesson_max_score=lesson_max_score[0] if lesson_max_score else 0

    if (lesson_max_score // 2 <= lesson_user_score):
        user_lesson_id = update_user_lesson(conn, lesson_id, session['user_id'])
        session['lesson_id'] = user_lesson_id

    html = render_template(
        'task_dialogue.html',
        theory_tasks_in_menu=theory_tasks_in_menu,
        page_title=page_title,
        dialogue_task=dialogue_task,
        voc_tasks_in_menu=voc_tasks_in_menu,
        dialogue_index=dialogue_index,
        short_lesson_description=short_lesson_description,
        task_description=task_description,
        max_task_score=max_task_score,
        my_task_score=my_task_score,
        lesson_user_score=lesson_user_score,
        lesson_max_score=lesson_max_score,
        dialog_task_in_menu=dialog_task_in_menu,
        complete_sentence_task_in_menu=complete_sentence_task_in_menu,
        missing_word_task_in_menu=missing_word_task_in_menu,
        complete_dialog_task_in_menu=complete_dialog_task_in_menu,
        complete_dialog_task_with_words_in_menu=complete_dialog_task_with_words_in_menu,
        writing_exercise_in_menu=writing_exercise_in_menu,
    )
    
    return html