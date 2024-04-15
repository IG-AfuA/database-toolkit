from __future__ import annotations # https://stackoverflow.com/questions/62521777/how-to-declare-python-dataclass-member-field-same-as-the-dataclass-type
import json
from dataclasses import dataclass
import re

# TODO:
# - Translate $>>$ and $<<$
# - Translate < and >

BASE_URL = '...'

def html_to_bbcode(html_str: str):
    html_str = re.sub(r'<br>', '\n', html_str)
    html_str = re.sub(r'<strong>(.*?)</strong>', r'[b]\1[/b]', html_str)
    html_str = re.sub(r'<code>(.*?)</code>', r'[color=#ff1493]\1[/color]', html_str)
    html_str = re.sub(r'<img src="(.*?)">', '[img]'+BASE_URL+r'\1[/img]', html_str)

    return html_str

def latex_to_bbcode(text: str):

    def _latex_to_bbcode(match:re.Match):
        text = match.group(0)[1:-1]
        # This should be done with a recursive parser to capture
        # pairs of {} parentheses easily. Since we don't have that,
        # we need to ensure that parentheses are not nested while
        # substituting (e.g. with [^{]*).
        text = re.sub(r'\\,', '', text)                         # Commas separating thousandth, as in 4,200,000
        text = re.sub(r'\\pi', 'π', text)
        text = re.sub(r'\\lambda', 'λ', text)
        text = re.sub(r'\\Delta ?', 'Δ', text)
        text = re.sub(r'\\Omega ?', 'Ω', text)

        text = re.sub(r'\\approx', '≈', text)
        text = re.sub(r'\\cdot{}', '·', text)
        text = re.sub(r'\\cdot ?', '·', text)
        text = re.sub(r'\^{\\circ}', '°', text)                 # Degree sign (for angle)

        text = re.sub(r'\^{([^{]*?)}', r'[sup]\1[/sup]', text)
        text = re.sub(r'\^([^{])', r'[sup]\1[/sup]', text)

        text = re.sub(r'\\frac{([^{]*?)}{(.)}', r'\1÷\2', text)
        text = re.sub(r'\\frac{(.)}{([^{]*?)}', r'\1÷(\2)', text)

        text = re.sub(r'_{\\text{([^{]*?)}}', r'[sub]\1[/sub]', text)
        text = re.sub(r'_\\text{([^{]*?)}', r'[sub]\1[/sub]', text)
        text = re.sub(r'_([^{\\])', r'[sub]\1[/sub]', text)
        text = re.sub(r'_{([^{]*?)}', r'[sub]\1[/sub]', text)

        text = re.sub(r'\\text{(.)}', r'\1', text)
        text = re.sub(r'\\text{([^{_]*?)}', r'\1', text)

        text = re.sub(r'\\sqrt{([^{_]*?)}', r'[sqr]\1[/sqr]', text)

        # Repeat these instead of recursive context-free approach
        text = re.sub(r'\\frac{([^{]*?)}{(.)}', r'\1÷\2', text)
        text = re.sub(r'\\frac{(.)}{([^{]*?)}', r'\1÷(\2)', text)

        return text

    return re.sub(r'\$(.*?)\$', _latex_to_bbcode, text)

def latex_dollar_to_pars(latex_str: str):
    return re.sub(r'\$(.*?)\$', r'\\(\1\\)', latex_str)

# This can be used for debugging
def print_latex(text: str):
    inline_latex = r'\$(.*?)\$'
    eqs = re.findall(inline_latex, text)
    for eq in eqs:
        print(eq)
    return(text)

def extract_image(text: str):
    image_tag = r'<img src="[^"]*">'
    image_tags = re.findall(image_tag, text)
    assert(len(image_tags) < 2)
    if len(image_tags) == 0:
        return text, ''
    else:
        return re.sub(image_tag, '', text), image_tags[0]

class json_parser:
    def __init__(self):
        fh = open('afu-group-trainer/backend/assets/Fragenkatalog.json')
        question_pool = json.load(fh)
        fh.close()

        root = question_pool['children']
        self.novice_tree = root[0]
        self.cept_tree = root[1]
        self.text_processors = []

    def attach_text_processor(self, p):
        self.text_processors.append(p)

    def novice_questions(self):
        questions = []
        self._parse_tree(self.novice_tree, None, questions)
        return questions

    def cept_questions(self):
        questions = []
        self._parse_tree(self.cept_tree, None, questions)
        return questions


    def _parse_tree(self, node, category, questions):
        if len(node['children']) == 0:
            new_category = exam_category(category_id = node['id'][2:], category_name = node['name'], parent = category)
            self._extract_questions(node['questions'], new_category, questions)
        else:
            assert len(node['questions']) == 0
            new_category = exam_category(category_id = node['id'][2:], category_name = node['name'], parent = category)
            for child in node['children']:
                self._parse_tree(child, new_category, questions)

    def _extract_questions(self, node, category, questions):
        for question in node:
#           print(question['id'])
            q = exam_question(question_id = question['id'],
                              question_text = self._process_text(question['question']),
                              answer_0 = self._process_text(question['answers'][0]),
                              answer_1 = self._process_text(question['answers'][1]),
                              answer_2 = self._process_text(question['answers'][2]),
                              answer_3 = self._process_text(question['answers'][3]),
                              outdated = question['outdated'],
                              parent = category)
            questions.append(q)

    def _process_text(self, text):
        for p in self.text_processors:
            text = p(text)
        return text

@dataclass
class exam_category:
    category_id: str
    category_name: str
    parent: exam_category

    @property
    def category(self):
        return self.category_id + ': ' + self.category_name

@dataclass
class exam_question:
    question_id: str
    question_text: str
    answer_0: str
    answer_1: str
    answer_2: str
    answer_3: str
    outdated: bool
    parent: exam_category

    @property
    def category(self):
        return self.parent.category

    @property
    def parent_category(self):
        return self.parent.parent.category

    @property
    def question_with_id(self):
        return f'{self.question_id}: {self.question_text}'
