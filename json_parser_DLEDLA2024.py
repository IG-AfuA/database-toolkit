# This code needs major cleanup before it can be merged


from __future__ import annotations # https://stackoverflow.com/questions/62521777/how-to-declare-python-dataclass-member-field-same-as-the-dataclass-type
import json
from dataclasses import dataclass
import re

# TODO:
# Check if the following still holds for the 2024 version of the catalog
# - Translate $>>$ and $<<$
# - Translate < and >

# In case your export file will contain links to images, you
# have to specity a base URL here. This would be needed for, e.g., the classmarker
# export where images are pulled from an external web page. The base URL needs to
# start with 'https://' and have a trailing slash, e.g.
# 'https://classmarker.example.com/static/'. In this case, the following path
# is expected to exist and to containing the images:
# https://classmarker.example.com/static/img/
# You can pull these files from FIXME

BASE_URL = '/static/'

def eszett_to_ss(text: str):
    return re.sub(r'ß', 'ss', text)

# Converts $...$ to \(...\)
def latex_dollar_to_pars(latex_str: str):
    return re.sub(r'\$(.*?)\$', r'\\(\1\\)', latex_str)

# This can be used for debugging
def print_latex(text: str):
    inline_latex = r'\$(.*?)\$'
    eqs = re.findall(inline_latex, text)
    for eq in eqs:
        print(eq)
    return(text)

class json_parser:
    def __init__(self):
        fh = open('input-files/50ohm-pocket-main/assets/questions/E.json')
        question_pool = json.load(fh)
        self.novice_tree = question_pool['sections']
        fh.close()

        fh = open('input-files/50ohm-pocket-main/assets/questions/A.json')
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

    # FIXME: static
    def _merge_answer_text_image(self, question, answer_key, picture_key):
        text = question[answer_key]
        if text is None:
            # Typically when answer consist of images only
            text = ''
        else:
            text = self._process_text(text)

        if picture_key in question:
            img = question[picture_key]
            text += f'\n<img src="/static/img_DL24/{img}.svg" alt="{img}">'

        return text

    def _parse_tree(self, tree, questions):
        # We assume exactly two sets of nested 'sections' lists.
        for category in tree:
            for subcategory in category['sections']:
                for question in subcategory['questions']:
                    question_text = self._process_text(question['question'])
                    if 'picture_question' in question:
                        img = question['picture_question']
                        question_text += f'\n<br><img src="/static/img_DL24/{img}.svg" alt="{img}">'

                    answer0 = self._merge_answer_text_image(question, 'answer_a', 'picture_a')
                    answer1 = self._merge_answer_text_image(question, 'answer_b', 'picture_b')
                    answer2 = self._merge_answer_text_image(question, 'answer_c', 'picture_c')
                    answer3 = self._merge_answer_text_image(question, 'answer_d', 'picture_d')

                    q = exam_question(question_id = question['number'],
                              question_text = question_text,
                              answer_0 = answer0,
                              answer_1 = answer1,
                              answer_2 = answer2,
                              answer_3 = answer3,
                              category = eszett_to_ss(category['title']),
                              subcategory = eszett_to_ss(subcategory['title']))
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
