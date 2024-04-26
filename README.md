Overview
========

This repository contains tools to process questions for the amateur radio exam that are published in [the following repository](https://github.com/ccoors/afu-group-trainer) by Christian F Coors. Thus, you are expected to check out this repository in the root folder. A git submodule is in place for this purpose. In consequence, we recommend to check out the codebase using

```
$ git clone --recurse-submodules https://github.com/IG-AfuA/database-toolkit.git
```

or, alternatively,

```
$ git clone https://github.com/IG-AfuA/database-toolkit.git
$ cd database-toolkit
$ git submodule update --init --recursive
```


Converter for Moodle
====================

`convert_to_moodle.py` is used to produce a collection of questions for import
into Moodle.


Converter for ClassMarker
=========================

`convert_to_classmarker.py` is used to produce a collection of questions for
import into [ClassMarker](https://www.classmarker.com/). Note that you have to
set `BASE_URL` in `json_parser.py` to point to some web server that delivers
the images via https.

Thus, the base URL needs to start with `https://` and have a trailing slash,
e.g. `https://classmarker.example.com/static/`. In this case, the following
paths are expected to exist, containing the images and 'Lichtblicke',
respectively:
```
https://classmarker.example.com/static/img/
https://classmarker.example.com/static/lichtblicke/
```

You can pull these files from `afu-group-trainer/frontend/static/`


Rescaling Images
================

Some images have a fairly large resolution. `rescale_large_images.sh` is a helper script used to shrink those images.


Text Comparison
===============
    
`analyze_similarities.py` is used for text comparisons between the two question
pools. The Levenshtein similarity, longest common substring and cosine
similarity is computed for each pair of questions from the respective pools.
This is done for the question text alone ("Q") and also for the concatenation
of questions and answers ("QA"). HTML tags are stripped before comparison.
    
This can be useful to identify identical or similar questions, thus helping in
structuring courses where the novice license is acquired first, followed by an
upgrade class.
    
Running the program involves many pairwise comparisons, thus you cannot expect
this to be quick.

JSON Parser
-----------
`json_parser.py` is used by the conversion and analysis scripts. The file
contains a class that reads the json file from the afu-group-trainer by
ccoors and offers ways to iterate through the questions. It also contains
data structures to store question exams and answers.

This file is not meant to be used directly, but instead imported and used
by other conversion and analysis scripts.
