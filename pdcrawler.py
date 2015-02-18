import re, sys, getopt, urllib, urllib2
from pdparser import PDParser

#https://polldaddy.com/surveys/2008703/report/participants?view_type=all
#/surveys/2008703/report/107552652?view_type=all
#/surveys/2008703/report/participants?paged=2&view_type=all

def main(argv):
    opts, args = getopt.getopt(argv,"s:h",[])
    opt_dict = {}
    for opt, arg in opts:
        opt_dict[opt]=arg

    if '-s' in opt_dict:
        parser = PDParser(survey_num=opt_dict['-s'].strip('='))
    else:
        raise(Exception('Please provide a survey number using -s=<number> option'))

    #get participants and more participants pages
    #with open('participants.htm','r') as f:
    #    file_str = f.read()
    #    parser.feed(file_str)
    #print parser.participant_links
    #print parser.participant_pages

    with open('107734003.htm','r') as f:
        file_str = f.read()
        parser.feed(file_str)
        print parser.participant_id
        print parser.participant_data

if __name__ == "__main__":
   main(sys.argv[1:])