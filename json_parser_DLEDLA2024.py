# Mat says:
# This code needs major cleanup before it can be merged

# Standard packages:
from __future__ import annotations # https://stackoverflow.com/questions/62521777/how-to-declare-python-dataclass-member-field-same-as-the-dataclass-type
import json
from dataclasses import dataclass
import re

# Project files:
from toolkit_system import dev_print
from json_parser import (eszett_to_ss, latex_to_utf8, latex_to_utf8_subsuperscript, to_card2brain,
                         extract_image, math_signs_much_less_n_much_greater,
                         remove_flaws_coming_from_json_source, remove_flaws_in_plain_text,
                         latex_frac_to_dfrac)  # FIXME Issue #12

# TODO:
# Check if the following still holds for the 2024 version of the catalog
# - Translate $>>$ and $<<$
# - Translate < and >

# In case your export file will contain links to images, you
# have to specify a base URL here. This would be needed for, e.g., the classmarker
# export where images are pulled from an external web page. The base URL needs to
# start with 'https://' and have a trailing slash, e.g.
# 'https://classmarker.example.com/static/'. In this case, the following path
# is expected to exist and to containing the images:
# https://classmarker.example.com/static/img/
# You can pull these files from

BASE_URL = 'https://classmarker.example.com/static/'

# Check BASE_URL
assert(BASE_URL.startswith('https://'))
assert(BASE_URL.endswith('/'))


# This can be used for debugging
# def print_latex(text: str):
#    inline_latex = r'\$(.*?)\$'
#    eqs = re.findall(inline_latex, text)
#    for eq in eqs:
#        print(eq)
#    return text


# Structure of the JSON files in
# input-files/50ohm-pocket/assets/questions/
#
# - "sections" = [
#    - "sections" = [
#       - "questions" = [
#
# fields of a single data set:
# allways:          'number'           consisting of 2 capital letters + 3 digits
# allways:          'class'            = '1', '2' or '3' (for 'Klasse N', 'E' or 'A')
# allways:          'question'         string
# allways:          'answer_a'         string, if there is an image, then content = "" or NULL
# allways:          'answer_b'         dito
# allways:          'answer_c'         dito
# allways:          'answer_d'         dito
# if applicable:   'picture_question'  = number + '_q'. This is the name of the image file (without the ending '.svg')
# if applicable:   'picture_a'         = number + '_a'. dito
# if applicable:   'picture_b'         = number + '_b'. dito
# if applicable:   'picture_c'         = number + '_c'. dito
# if applicable:   'picture_d'         = number + '_d'. dito

class json_parser:
    def __init__(self):
        fh = open('input-files/50ohm-pocket/assets/questions/NE.json')
        question_pool = json.load(fh)
        self.novice_tree = question_pool['sections']
        fh.close()

        fh = open('input-files/50ohm-pocket/assets/questions/A.json')
        question_pool = json.load(fh)
        self.cept_tree = question_pool['sections']
        fh.close()

        self.text_processors = [eszett_to_ss, ] # Convert ß to ss by default

    def attach_text_processor(self, p):
        self.text_processors.append(p)

    def novice_questions(self):
        questions = []
        self._parse_tree(self.novice_tree, questions)
        return questions

    def cept_questions(self):
        questions = []
        self._parse_tree(self.cept_tree, questions)
        return questions

    def _merge_answer_text_image(self, question, answer_key, picture_key):
        text = question[answer_key]
        if text is None:
            # Typically when answer consist of images only
            text = ''
        else:
            text = self._process_text(text)

        if picture_key in question:
            text += '<img src="' + question[picture_key] +'.png">'

        return text

    def _parse_tree(self, tree, questions):
        # We assume exactly two sets of nested 'sections' lists.
        for category in tree:
            for subcategory in category['sections']:
                for question in subcategory['questions']:
                    question_text = self._process_text(question['question'])
                    if 'picture_question' in question:
                        img = question['picture_question']
                        question_text += f'<img src="{img}.png">'

                    answer0 = self._merge_answer_text_image(question, 'answer_a', 'picture_a')
                    answer1 = self._merge_answer_text_image(question, 'answer_b', 'picture_b')
                    answer2 = self._merge_answer_text_image(question, 'answer_c', 'picture_c')
                    answer3 = self._merge_answer_text_image(question, 'answer_d', 'picture_d')

                    q = exam_question(question_id = question['number'],
                              question_text = self._process_text(question_text),
                              answer_0 = self._process_text(answer0),
                              answer_1 = self._process_text(answer1),
                              answer_2 = self._process_text(answer2),
                              answer_3 = self._process_text(answer3),
                              category = self._process_text(category['title']),
                              subcategory = self._process_text(subcategory['title']))
                    # dev_print(q.question_id) #FIXME PEPE
                    # if q.question_id == "AD203": exit() #FIXME PEPE
                    questions.append(q)

    # Consecutively run each processor on text input
    def _process_text(self, text:str):
        for p in self.text_processors:
            text = p(text)
        return text

@dataclass
class exam_question:
    question_id: str
    question_text: str
    answer_0: str
    answer_1: str
    answer_2: str
    answer_3: str
    category: str
    subcategory: str
