from json_parser import json_parser, html_to_bbcode, latex_to_bbcode
import csv

# See https://www.classmarker.com/docs/importquestions/classmarker-multiple-choice-question-type-instructions.pdf
def write_csv(filename, questions, pool):
    filename_counter = 0
    i = None
    csvfile = None
    for q in questions:
        # Split into batches of 50 as per instructions
        if i is None or i >= 50:
            i = 0
            if csvfile is not None:
                csvfile.close()

            csvfile = open(filename.format(filename_counter), 'w')
            filename_counter += 1
            writer = csv.writer(csvfile)
            writer.writerow(['Question Type: multiplechoice','Parent Category',' Category','Random Answers','Correct Feedback','Incorrect Feedback','Points','Question','Correct','Answer A','Answer B','Answer C','Answer D'])

        writer.writerow(['multiplechoice',pool,q.parent.category_id,'Yes','','',1,q.question_with_id,'A',q.answer_0,q.answer_1,q.answer_2,q.answer_3])
        i+= 1


qp = json_parser()
qp.attach_text_processor(html_to_bbcode)
qp.attach_text_processor(latex_to_bbcode)
write_csv('classmarker_export_hb3_{:03d}.csv', qp.novice_questions(), 'BNetzA Klasse E')
write_csv('classmarker_export_hb9_{:03d}.csv', qp.cept_questions(), 'BNetzA Klasse A')
