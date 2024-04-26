from json_parser import json_parser

qp = json_parser()

categories = set()

for q in qp.novice_questions():
    categories.add('D'+q.parent.category_id)

for q in qp.cept_questions():
    categories.add('D'+q.parent.category_id)

[print(i) for i in sorted(categories)]
