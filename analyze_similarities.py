from json_parser import json_parser
from strsimpy.normalized_levenshtein import NormalizedLevenshtein
from strsimpy.longest_common_subsequence import LongestCommonSubsequence
from strsimpy.cosine import Cosine

import xlsxwriter
import re

normalized_levenshtein = NormalizedLevenshtein()
lcs = LongestCommonSubsequence()
cos = Cosine(1)


workbook = xlsxwriter.Workbook('HB3_HB9_textdistance.xlsx')
worksheet = workbook.add_worksheet('Vergleich')

title = ('HB3', 'HB9', 'Levenshtein Q', 'LCS Q', 'Cosine Q', '', 'Levenshtein QA', 'LCS QA', 'Cosine QA')
title_format = workbook.add_format({'bold': True})
worksheet.write_row(0, 0, title, title_format)

clean = re.compile('<.*?>')

qp = json_parser()

def eliminate_html(string):
    return re.sub(clean, '', string)

# Preparation step: Assemble strings
# q:  questions
# qa: concatenated questions and answers
hb3_id = []
hb9_id = []
hb3_q  = []
hb9_q  = []
hb3_qa = []
hb9_qa = []
for q in qp.novice_questions():
    text_hb3_q = eliminate_html(q.question_text)
    hb3_q.append(text_hb3_q)
    text_hb3_qa = ''.join((text_hb3_q,
                           eliminate_html(q.answer_0),
                           eliminate_html(q.answer_1),
                           eliminate_html(q.answer_2),
                           eliminate_html(q.answer_3)))
    hb3_qa.append(text_hb3_qa)
    hb3_id.append(q.question_id)

for q in qp.cept_questions():
    text_hb9_q = eliminate_html(q.question_text)
    hb9_q.append(text_hb9_q)
    text_hb9_qa = ''.join((text_hb9_q,
                           eliminate_html(q.answer_0),
                           eliminate_html(q.answer_1),
                           eliminate_html(q.answer_2),
                           eliminate_html(q.answer_3)))
    hb9_qa.append(text_hb9_qa)
    hb9_id.append(q.question_id)

counter = 1
for hb3_id_text, hb3_q_text, hb3_qa_text in zip(hb3_id, hb3_q, hb3_qa):
    for hb9_id_text, hb9_q_text, hb9_qa_text in zip(hb9_id, hb9_q, hb9_qa):

        q_lvst_score = normalized_levenshtein.similarity(hb3_q_text, hb9_q_text)
        q_lcs_score  = lcs.length(hb3_q_text, hb9_q_text)
        q_cos_score  = cos.similarity(hb3_q_text, hb9_q_text)

        qa_lvst_score = normalized_levenshtein.similarity(hb3_qa_text, hb9_qa_text)
        qa_lcs_score  = lcs.length(hb3_qa_text, hb9_qa_text)
        qa_cos_score  = cos.similarity(hb3_qa_text, hb9_qa_text)

        worksheet.write_row(counter, 0, (hb3_id_text, hb9_id_text, q_lvst_score, q_lcs_score, q_cos_score, '', qa_lvst_score, qa_lcs_score, qa_cos_score))
        counter += 1
        # Update on progress (we make almost 400000 comparisons)
        if counter % 10000 == 0: print(counter)

workbook.close()
