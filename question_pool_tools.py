


# Dictionary of allowed command line arguments
# Values are needed for:
# -- part of file path names
# -- info in the Excel in the field 'Ergänzung A'
dict_arguments  = {
    "-e06":"DLE-2006",
    "-a07":"DLE-2007",
    "-e24":"DLE-2024",
    "-a24":"DLA-2024",
    "-beta":"BETA"
}

ACTIVE_POOL = ""

def set_active_pool(pool : str):
    global ACTIVE_POOL
    ACTIVE_POOL = pool

def active_pool():
    return ACTIVE_POOL

def check_active_pool(pool_list: list):
    return ACTIVE_POOL in pool_list

def check_arguments(arguments):
    count_error = 0
    if '-beta' in arguments:
        maximal_arg = 2
    else:
        maximal_arg = 1
    if len(arguments) < (maximal_arg + 1):
        # sys.argv[0] contains path and script name
        # arguments in sys.argv[1] and following
        print_separation_line()
        print("Please provide at least one question pool as command line argument.")
        print_separation_line()
        print_arguments()
        print_separation_line()
        exit()
    else:
        for string_element in arguments[1:]:
            if string_element in list(dict_arguments.keys()):
                pass
            else:
                count_error += 1
                print_separation_line()
                print("Error: '" + string_element + "' is not a correct command line argument.")
    if count_error > 0:
        print_separation_line()
        print_arguments()
        print_separation_line()
        exit()

    # FIXME temporary restriction
    # source code can so far only handle one question pool
    if len(arguments) > (maximal_arg + 1):
        print_separation_line()
        print("*** temporary restriction ***")
        print("Please provide with exact one question pool argument")
        print("and additional as second argument is only '-beta' possible.")
        print_separation_line()
        print_arguments()
        print_separation_line()
        exit()


def print_arguments():
    print("Possible command line arguments are:")
    print("-e06 : Export question pool year 2006 for Novice Licence from BNetzA Germany")
    print("-a07 : Export question pool year 2007 for Advanced Licence from BNetzA Germany")
    print("-e24 : Export question pool year 2024 for Novice Licence from BNetzA Germany")
    print("-a24 : Export question pool year 2024 for Advanced Licence from BNetzA Germany")
    print("-beta : Only some typical examples from the selected question pool will be exported")


def print_separation_line():
    print("--------------------------------")


def beta_test_exam_questions(question : str):

    if check_active_pool(['-e06']):
        selection = [
            "TA104",    # answer with superscript
            "TB105",    # answers with very long texts
            "TB604",    # answers with number with kommas
            "TB610",    # question with image in squre
            "TB902",    # answers with math term
            "TC105",    # answer with image in portrait
            "TC106",    # answers are images in portrait
            "TC203",    # question with text and small image
            "TC301",    # question with text and image in landscape
            "TC506",    # each answer has text, an immage in the middle and again text
            "TC612",    # answer with 1, 2, 3
            "TD102",    # question with text and middle size image; Omega   sign in question and answer; subscript in question
            "TD203",    # answers with wide images
            "TE307",    # short question; short answers
            "TF205",    # question with a lage image
            "TH201",    # answers with lamda / 2 term
            "TH205",    # answers with %
            "TI204",    # answer with 4 digit numbers
            "TL201",    # answer with long math term
            "TL202",    # answer with long math term
            "TL302"    # answer with superscript
        ]
        return question in selection

    elif check_active_pool(['-a07']):
        selection = [
            "TA105",    # answers with math terms
            "TA113",    # answers with superscript and comma in superscript
            "TA116",    # answers with numbers and comma
            "TA117",    # answer with %
            "TA118",    # answers with long numbers
            "TA122",    # answers with lamda-sign
            "TB102",    # answers with Omega-sign
            "TB106",    # long answers
            "TB111",    # picture in question and long answers
            "TB207",    # answers with R_L and R_i
            "TB209",    # answers with << and >>
            "TB601",    # answers with subscript
            "TB611",    # answers with Pi and math terms
            "TB909",    # answers with long math terms
            "TB910",    # answers with long math terms
            "TB923",    # answers with frac math terms
            "TC202",    # answers with images
            "TC206",    # answers with mycro
            "TC507",    # answers with image between text
            "TC511",    # big image in question; answers with 1,2,3
            "TC512",    # big image in question; answers with 1,2,3
            "TC513",    # big image in question; answers with 1,2,3
            "TC115",    # answers with big imaages
            "TC526",    # images in question and answer
            "TC601",    # answers with 1,2
            "TC619",    # big image in question
            "TC626",    # big images in question AND answers
            "TC716",    # big images in answers
            "TD108",    # answer with math term with /
            "TD204",
            "TD406",    # answers with 'sz' and v_u
            "TD605",
            "TE202",    # answers with math terms between text
            "TG101",    # question with big picture
            "TG111",    # question with big picture
            "TG223",    # question with big picture
            "TG233",    # answers with long texts
            "TG315",    # answers with C_load
            "TG316",    # answers with C_1
        ]
        return question in selection

    else:
        print_separation_line()
        print("Pool unbekannt in question_pool_tools, def beta_test...")
        print_separation_line()
        return True     # every question is accepted
