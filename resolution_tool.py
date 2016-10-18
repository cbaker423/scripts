import os
import sys
import argparse
from collections import OrderedDict

######### PROMPTS #########
HEADER = '********************************************Resolution/Closure of Issue ***********************************************************'
FOOTER = '***********************************************************************************************************************************\n'
SUMMARY_KEY = "Summary of issue: "
RESOLUTION_KEY = "Resolution: "
Q1 = "1.    Is there a runbook or other set of steps that need to be documented to resolve if this recurs? If yes, please post link to runbook/documentation. "
Q2 = "2.    Could this problem have been identified through monitoring/alerts? "
Q3 = "3.    Could this problem have been automatically resolved through programmatic means? "
Q4 = "4.    Is the problem permanently resolved so it does not reappear? If so, how is it permanently resolved? "
Q5 = "5.    What visual checks of some metric, value, etc in Quicksilver would have helped in triage / resolution? "
RCA_KEY = "RCA: "
JIRA_KEY = "JIRA feature numbers that have been created as a result of the resolution of this problem: "

HELP_MSG = [(SUMMARY_KEY, "<please provide a brief summary of the problem>"),
            (RESOLUTION_KEY, "<please provide a brief summary of how you fixed the problem or how it was resolved>"),
            (Q1, "N/A"),
            (Q2, "N/A"),
            (Q3, "(For example, if a service needs to be restarted to correct an error, can we script that?  Could we script a restart, then check and only then if the service isn't up, do a call out?)"),
            (Q4, "(For example: simply re-distributing load to get things working w/o adding more capacity doesn't really resolve the problem.)"),
            (Q5, "(For example: When we ran out of  floating IPs, if we had counts in the dashboard of free floating IPs, this probably would have been obvious (if not caught earlier as it approached.)"),
            (RCA_KEY, "<please provide the root cause analysis of why this problem occurred>"),
            (JIRA_KEY, "Ensure these features are linked to this Bug.")]

FORM = [(SUMMARY_KEY, ""),
        (RESOLUTION_KEY, ""),
        (Q1, ""),
        (Q2, ""),
        (Q3, ""),
        (Q4, ""),
        (Q5, ""),
        (RCA_KEY, ""),
        (JIRA_KEY, "")]
###########################


######### OPTIONS #########
ISSUE_KEY = 'issue'
OUTPUT_DIR_KEY = 'log_dir'
PRINT_QUESTIONS_KEY = 'print_questions'

SHORT = 'short'
LONG = 'long'
HELP = 'help'
ACTION = 'action'
ARG_NAME = 'arg_name'
REQUIRED = 'required'
DEFAULT = 'default'
NARGS = 'nargs'
CONST = 'const'

PROG_DESC = "Prompt for filling out resolution/closure of issue"

OPTION_HELP = {
    ISSUE_KEY: 'Jira ticket id',
    OUTPUT_DIR_KEY: 'Directory where the output will be saved',
    PRINT_QUESTIONS_KEY: 'Print all questions, or specify comma delimited list (i.e. Q1,Q2,Q3)'
}

OPTS = {
        ISSUE_KEY: {
            SHORT: '-i',
            LONG: '--issue',
            HELP: OPTION_HELP[ISSUE_KEY],
            ACTION: None,
            ARG_NAME: 'issue',
            REQUIRED: True,
            DEFAULT: None,
            NARGS: 1,
            CONST: None
        },
        OUTPUT_DIR_KEY: {
            SHORT: '-o',
            LONG: '--output-dir',
            HELP: OPTION_HELP[OUTPUT_DIR_KEY],
            ACTION: None,
            ARG_NAME: 'output_dir',
            REQUIRED: False,
            DEFAULT: './',
            NARGS: 1,
            CONST: None
        },
        PRINT_QUESTIONS_KEY: {
            SHORT: '-q',
            LONG: '--print-questions',
            HELP: OPTION_HELP[PRINT_QUESTIONS_KEY],
            ACTION: None,
            ARG_NAME: 'print_questions',
            REQUIRED: False,
            DEFAULT: None,
            NARGS: '?',
            CONST: 'all'
        }
}
###########################

###### OTHER CONSTS #######
FILENAME = '-resolution.txt'
FILE_EXITS_WARNING = 'Resolution file for this issue already exists; continuing will overwrite.. Do you wish to continue? (y/n) '
QUESTION_LIST_DEFAULT = 'all'
###########################


def prompt_user(form, help_msg):
    for key in form:
        form[key] = raw_input(key)
        while str(form[key]).lower() == 'help' or str(form[key]).lower() == 'h':
            print help_msg[key]
            form[key] = raw_input(key)
    return form

def write_to_file(filename, form):
    f = open(filename, 'w')
    f.write(HEADER + '\n')
    for key in form:
        if key == Q1:
            f.write('\nPlease answer the following questions and provide details:\n')
        f.write(key + "\n      " + form[key] + "\n")
    f.write(FOOTER)
    f.close()
    print "Resolution saved to: " + filename
    return 0

def print_template_questions(questions, form):
    if str(questions).lower() == QUESTION_LIST_DEFAULT:
        for key in form:
            print key
    else:
        qlist = str(questions).upper().split(',')
        for q in qlist:
            try:
                print eval(q)
            except NameError, e:
                print("No question labeled " + q)
                return 1
    return 0

def main(args):
    form = OrderedDict(FORM)
    help_msg = OrderedDict(HELP_MSG)

    if args.print_questions:
        status = print_template_questions(args.print_questions, form)
        sys.exit(status)

    filename = str(args.output_dir).rstrip('/') + '/' +  str(args.issue) + FILENAME
    if os.path.isfile(filename) is True and str(raw_input(FILE_EXITS_WARNING)).lower() == 'n':
        print "Goodbye"
        sys.exit(1)
    completed_form = prompt_user(form, help_msg)
    status = write_to_file(filename, completed_form)
    sys.exit(status)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     usage='%(prog)s [options]',
                                     description=PROG_DESC)

    for opt in OPTS:
        option = OPTS[opt]
        parser.add_argument(option[SHORT], option[LONG],
                            help=option[HELP], action=option[ACTION],
                            required=option[REQUIRED],
                            default=option[DEFAULT],
                            nargs=option[NARGS], const=option[CONST])
    args = parser.parse_args()
    main(args)
