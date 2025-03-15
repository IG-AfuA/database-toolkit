# no IMPORT needed

def print_arguments():
    print("Possible command line arguments are:")
    print("-?   : Is showing this overview of possible arguments")
    print("-e06 : Export question pool year 2006 for Novice Licence from BNetzA Germany")
    print("-a07 : Export question pool year 2007 for Advanced Licence from BNetzA Germany")
    print("-e24 : Export question pool year 2024 for Novice Licence from BNetzA Germany")
    print("-a24 : Export question pool year 2024 for Advanced Licence from BNetzA Germany")
    print("And only for beta testing: either '-beta' or '-math'")
    print("-beta : Only some typical examples from the selected question pool will be exported")
    print("-math : Only questions containing LaTex code will be exported")

def print_separation_line():
    print("--------------------------------")

# Dictionary of allowed command line arguments
# Values are needed for:
# -- part of file path names
# -- info in the Excel in the field 'Ergänzung A'
dict_arguments  = {
    "-e06":"DLE-2006",
    "-a07":"DLA-2007",
    "-e24":"DLE-2024",
    "-a24":"DLA-2024",
    "-beta":"ONLY-FOR-BETA-TESTING",
    "-math":"ONLY-FOR-BETA-TESTING"
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

    if '-?' in arguments:
        print_separation_line()
        print_arguments()
        print_separation_line()
        exit()

    if '-beta' in arguments and '-math' in arguments:
        print_separation_line()
        print("'-beta' and '-math' can not be used together")
        print_separation_line()
        print_arguments()
        print_separation_line()
        exit()

    if '-beta' in arguments or '-math' in arguments:
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


def beta_test_exam_questions(question : str):

    if check_active_pool(['-e06']):
        selection = [
            "TA104",    # answer with superscript
            "TB105",    # answers with very long texts
            "TB604",    # answers with number with kommas
            "TB610",    # question with image in square
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
            "TI204",    # answer with 4-digit numbers
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
            "TC206",    # answers with micro
            "TC507",    # answers with image between text
            "TC511",    # big image in question; answers with 1,2,3
            "TC512",    # big image in question; answers with 1,2,3
            "TC513",    # big image in question; answers with 1,2,3
            "TC115",    # answers with big images
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

    elif check_active_pool(['-e24']):
        selection = [
            "EA108",    # answers with superscript
            "EA112",    # answer with omega sign
            "EA113",    # answer with micro sign
            "EA116",    # answers with long numbers
            "EB203",    # question with small image; answers with /
            "EB303",    # answers with °
            "EB305",    # one answer with lamda sign
            "EB310",    # question with big image im portrait format
            "EB411",    # question with big image
            "EB505",    # answers with square root math term
            "EB506",    # answers with math term
            "EC110",    # answers with small images
            "EC113",    # answer with numbers and omega sign
            "EC115",    # question with small image
            "EC301",    # answers with big images
            "EC306",    # question with 2 images, different size
            "EC506",    # question with big image
            "EC512",    # answers with images between text
            "EC516",    # answers with omega sign and /
            "EC520",    # big images as answers
            "EC609",    # answers with 1,2,3
            "ED101",    # answers with frac math term
            "ED120",    # answers with micro signs
            "EE101",    # answer with images im landscape format
            "EE203",
            "EE403",    # question with 'sz'; answer with square root
            "EF309",    # question with big image
            "EG102",    # answers with lamda sign
            "EG111",    # image in question should be one big image
            "EG502"    # answers with long math terms
        ]
        return question in selection

    elif check_active_pool(['-a24']):
        selection = [
            "AB103",    # Testen frac --> dfrag #FIXME
            "AB104",    # answers with long texts
            "AB208",    # answers with omega signs
            "AC304",    # 'kOhm.' in question
            "AC405",    # images in question and answers #FIXME Bild von Frage fehlt
            "AC406",    # images in question and answers #FIXME Bild von Frage fehlt
            "AC515",    # 'kOhm' in answers #FIXME
            "AC522",    # 'kOhm ' und 'kOhm;' in question #FIXME
            "AC523",    # 'm\Omega' in question #FIXME
            "AD109",    # question with image in landscape format #FIXME 'kOhm' in Frage
            "AD110",    # ERROR missing subscript in answers # FIXME
            "AD111",    # ERROR missing subscript in answers # FIXME
            "AD113",    # kOhm; und kOhm. # FIXME
            "AD114",    # question with image in portrait format
            "AD305",    # square size images in all answers
            "AD307",    # images in landscape format in all answers
            "AD308",    # images in question and answers #FIXME
            "AD402",    # questions and answers with v_U #FIXME utf/LaTex-Combo
            "AD406",    # images in question and answers #FIXME Bild von Frage fehlt
            "AD408",    # images in question and answers #FIXME Bild von Frage fehlt
            "AD410",
            "AD416",    # ERROR missing subscript in answers # FIXME
            "AF120",    # question with large size image in landscape format
            "AF210",    # question with large size image in landscape format
            "AF314",    # ERROR answers #FIXME
            "AF426",    # question with big square size image
            "AG502",    # question with long math term #FIXME
            "AH102",    # answers with long texts
            "AH204",    # question with foF2, #FIXME
            "AH206",    # answers with f_opt, f_krit, foF2, #FIXME
            "AK103"     # testen frac --> dfrac
        ]
        return question in selection

    else:
        print_separation_line()
        print("ERROR in modul question_pool_tools.py")
        print("Question pool unknown in def beta_test_exam_question()")
        print_separation_line()
        return True     # True = every question is accepted
