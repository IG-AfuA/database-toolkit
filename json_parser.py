# Standard packages:
from __future__ import annotations # https://stackoverflow.com/questions/62521777/how-to-declare-python-dataclass-member-field-same-as-the-dataclass-type
import json
from dataclasses import dataclass
import re

# Project
from toolkit_system import dev_print

# Sample how math terms can be used in Card2Brain app in the question field.
# <p><span class="math-tex">\(\frac{P}{U^2} = R\)</span></p>


# FIXME @Mats: Is this note still needed?
# - Translate $>>$ and $<<$
# - Translate < and >


# In case your export file will contain links to images or 'Lichtblicke', you
# have to specify a base URL here. This would be needed for, e.g., the classmarker
# export where images are pulled from an external web page. The base URL needs to
# start with 'https://' and have a trailing slash, e.g.
# 'https://classmarker.example.com/static/'. In this case, the following paths
# are expected to exist, containing the images and 'Lichtblicke', respectively:
# https://classmarker.example.com/static/img/
# https://classmarker.example.com/static/lichtblicke/
# You can pull these files from ./afu-group-trainer/frontend/static/

BASE_URL = 'https://classmarker.example.com/static/'

# Check BASE_URL
assert(BASE_URL.startswith('https://'))
assert(BASE_URL.endswith('/'))


# ===================================
# START of function definitions
# ===================================

# Exchange the german letter 'ß' with 'ss' as used in Switzerland:
def eszett_to_ss(text: str):
    return re.sub(r'ß', 'ss', text)


# '≪' and '≫' instead of '<<' and '>>'
def math_signs_much_less_n_much_greater(text: str):
    text = re.sub(r'<<','≪', text)
    text = re.sub(r'>>', '≫', text)
    return text


# In question pool DL-2024 we have some flaws,
# which have to be removed:
def remove_flaws_coming_from_json_source(text: str):

    # Flaw in DL-2024 question pools:
    # change '\[ ... \]' to '<br>$ ... $<br>' because Card2Brain app can't handle '\[ ... \]'
    text = re.sub(r'\\\[', '<br>$', text)
    text = re.sub(r'\\\]', '$<br>', text)

    # Flaw in DL-2024 question pools:
    # incorrect LaTex term: '\kiloOhm' --> 'k\Omega'
    text = re.sub(r'\\kiloOhm', r'k\\Omega', text)

    # Flaw in DL-2024 question pools:
    # question pool contains in plain text: '\mOhm' --> ''mΩ'
    text = re.sub(r'\\mOhm', 'mΩ', text)

    # Flaw in DL-2024 question pools:
    # plain text: 'foF2' --> 'f₀F2'
    # Quote 50ohm.de:
    # > Als Formelzeichen verwendet man f₀ (kleiner tiefgestellter Buchstabe „O“ für ordinary wave) gefolgt von
    # > der ionosphärischen Region, für die diese Frequenz gilt, also z.B. f₀F2 für die F2-Region.
    text = re.sub('foF2', 'f₀F2', text)

    # Flaw in DL-2024 question pools:
    # plain text: 'kOhm' --> 'kΩ'
    text = re.sub('kOhm', 'kΩ', text)

    # Flaw in DL-2024 question pools:
    # remove space before angle-sign: '90 °' --> '90°'
    text = re.sub(' \u00b0', '\u00b0', text)

    return text


def remove_flaws_in_plain_text(text: str):

    # In 1 question in DLA-2024 is a '\Omega' in the plain text
    text = re.sub(r'\\Omega', 'Ω', text)  #

    return text


# Transform html-code to BBCode (e.g. used for ClassMaker):
def html_to_bbcode(html_str: str):
    html_str = re.sub(r'<br>', '\n', html_str)
    html_str = re.sub(r'<strong>(.*?)</strong>', r'[b]\1[/b]', html_str)
    html_str = re.sub(r'<code>(.*?)</code>', r'[color=#ff1493]\1[/color]', html_str)
    html_str = re.sub(r'<img src="(.*?)">', '[img]'+BASE_URL+r'img/\1[/img]', html_str)

    # FIXME: Move path 'BASE_URL' to 'convert_to_...'

    return html_str

#


# Transform Latex notation (of greek letters and math terms)
# to UTF8 notation:
def latex_to_utf8(text: str):

    def _latex_to_utf8(match:re.Match):
        text = match.group(0)
        text = re.sub(r'\\,', '', text)          # Commas separating thousandth, as in 4,200,000
        text = re.sub(r'\\pi', 'π', text)
        text = re.sub(r'\\lambda', 'λ', text)
        text = re.sub(r'\\Delta ?', 'Δ', text)
        text = re.sub(r'\\delta ?', 'δ', text)
        text = re.sub(r'\\phi ?', 'φ', text)
        text = re.sub(r'\\varphi ?', 'φ', text)
        text = re.sub(r'\\Omega ?', 'Ω', text)
        text = re.sub(r'\\approx', '≈', text)
        text = re.sub(r'\\cdot{}', '·', text)
        text = re.sub(r'\\cdot ?', '·', text)

        # Degree sign (for angle):
        text = re.sub(r'\^{\\circ}', '°', text)  # Notation in DLE2006/DLA2007 question pool
        text = re.sub(r'\^\\circ', '°', text)  # Notation in DLA2024 question pool

        if '\\' not in text and '_' not in text and '^' not in text:
            # String is latex-free now, so we can strip the dollars
            return text[1:-1]
        else:
            return text

    return re.sub(r'\$(.*?)\$', _latex_to_utf8, text)


# Transform Latex notation for superscript and subscript
# to UTF8 notation:
def latex_to_utf8_subsuperscript(text: str):
    def _latex_to_utf8_subsuperscript(match:re.Match):
        def _latex_to_utf8_superscript(match:re.Match):
            text = match.group(1)
            superscript_map = {
                '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
                'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ', 'f': 'ᶠ', 'g': 'ᵍ', 'h': 'ʰ', 'i': 'ⁱ', 'j': 'ʲ',
                'k': 'ᵏ', 'l': 'ˡ', 'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ', 'p': 'ᵖ', 'r': 'ʳ', 's': 'ˢ', 't': 'ᵗ', 'u': 'ᵘ',
                'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ', 'y': 'ʸ', 'z': 'ᶻ', '-': '⁻', ',': '_'
            }
            # WORKAROUND
            # In DLA-2007-TA113 is a comma in superscript as LaTex term.
            # But a comma in superscript does not exist in unicode. Therefore
            # in the map above a comma will be replaced by an underline.
            # And because of the underline the whole term will stay in LaTex, see below.

            return ''.join([superscript_map[i] for i in text])

        def _latex_to_utf8_subscript(match:re.Match):
            text = match.group(1)
            subscript_map = {
                '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
            }
            return ''.join([subscript_map[i] for i in text])

        text = match.group(0)

        # Let's make a backup of the LaTex term before transforming
        # superscript and subscript to utf8:
        save_text = text

        # Explanation of Regex syntax:
        # https://www.w3schools.com/python/python_regex.asp

        # Superscript:
        text = re.sub(r'\^{([^{}]+)}', _latex_to_utf8_superscript, text)
        text = re.sub(r'\^(.)', _latex_to_utf8_superscript, text)

        # Subscript: Only convert numbers:
        # because subscript numbers are accepted in Card2Brain answer fields
        text = re.sub(r'\_(\d)', _latex_to_utf8_subscript, text)

        # Only in question pool DLA-2024 exists:
        # 1) '$\textrm{R}_1$' or '$\textrm{R}_2$' or '$\textrm{R}_3$' or '$\textrm{R}_4$'
        # 2) '$\text{AP}_1$' or '$\text{AP}_2$' or '$\text{AP}_3$' or '$\text{AP}_4$'
        # With following two pattern these terms can be transformed free of LaTex:
        text = re.sub(r'\\textrm{R}', r'R', text)
        text = re.sub(r'\\text{AP}', r'AP', text)

        if '\\' not in text and '_' not in text and '^' not in text:
            # String is latex-free now, so we can strip the dollars
            return text[1:-1]
        else:
            # keep the original LaTex term if a complete transformation was not possible:
            return save_text


    return re.sub(r'\$(.*?)\$', _latex_to_utf8_subsuperscript, text)


# Transform Latex notation (for superscript, subscript and simple fractions):
# to BB-Code notation:
def latex_to_bbcode(text: str):

    def _latex_to_bbcode(match:re.Match):
        text = match.group(0)[1:-1] # Strip dollars
        # This should be done with a recursive parser to capture
        # pairs of {} parentheses easily. Since we don't have that,
        # we need to ensure that parentheses are not nested while
        # substituting (e.g. with [^{]*).

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


# Converts $...$ to \(...\)
def latex_dollar_to_pars(latex_str: str):
    return re.sub(r'\$(.*?)\$', r'\\(\1\\)', latex_str)


# Used to surround TeX equations with '<span class="math-tex">'
# tags, necessary in card2brain exports.
def to_card2brain(text:str):
    def _latex_to_card2brainmath(match:re.Match):
        text = match.group(0)[1:-1] # Strip dollars
        return '<span class="math-tex">\(' + text + '\)</span>'

    return re.sub(r'\$(.*?)\$', _latex_to_card2brainmath, text)


# All math terms with fraction shall use \dfrac instead of \frac:
def latex_frac_to_dfrac(latex_str:str):
    return re.sub(r'\\frac', r'\\dfrac', latex_str)


# This can be used for debugging
def print_latex(text: str):
    inline_latex = r'\$(.*?)\$'
    eqs = re.findall(inline_latex, text)
    for eq in eqs:
        print(eq)
    return(text)


# Extract the image name and return
#  a. the question text with removed image tag
#  b. the names of the removed images
def extract_image(text: str):
    image_tag = r'<img src="([^"]*)">'
    image_tags = re.findall(image_tag, text)
    if len(image_tags) == 0:
        return text, None
    else:
        # return:
        # a. Question with removed img tag
        # b. List auf image file names
        return re.sub(image_tag, '', text), image_tags


def prefix_static_image_path(text: str):
    return re.sub(r'<img src="(.*?)">', r'<img src="/static/img/\1">', text)

# ===================================
# END of function definitions
# ===================================

class json_parser:
    def __init__(self):
        fh = open('input-files/afu-group-trainer/backend/assets/Fragenkatalog.json')
        question_pool = json.load(fh)
        fh.close()

        root = question_pool['children']
        self.novice_tree = root[0]
        self.cept_tree = root[1]
        self.text_processors = [eszett_to_ss, ] # Convert ß to ss by default

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
        # Strip the first two chars from the category_id ('1.') and prefix
        # with '0' if id is single-digit (for easy ordering).
        category_id = node['id'][2:]
        if len(category_id) <= 1 or category_id[1] == '.':
            category_id = '0'+category_id
        if len(node['children']) == 0:
            new_category = exam_category(category_id = category_id, category_name = eszett_to_ss(node['name']), parent = category)
            self._extract_questions(node['questions'], new_category, questions)
        else:
            assert len(node['questions']) == 0
            new_category = exam_category(category_id = category_id, category_name = eszett_to_ss(node['name']), parent = category)
            for child in node['children']:
                self._parse_tree(child, new_category, questions)

    def _extract_questions(self, node, category, questions):
        for question in node:
            q = exam_question(question_id = question['id'],
                              question_text = self._process_text(question['question']),
                              answer_0 = self._process_text(question['answers'][0]),
                              answer_1 = self._process_text(question['answers'][1]),
                              answer_2 = self._process_text(question['answers'][2]),
                              answer_3 = self._process_text(question['answers'][3]),
                              outdated = question['outdated'],
                              parent = category)
            questions.append(q)

    # Consecutively run each processor on text input
    def _process_text(self, text:str):
        for p in self.text_processors:  #FIXME | Issue #20: Wie kann dies für Card2Brain gelöst
            text = p(text)              #FIXME | ohne die anderen Converter zu tangieren?
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
