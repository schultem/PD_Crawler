##
# Parse PollDaddy html for poll results or participant links.
#
# Saves multiple choice, answer-text, rank-report, and no-data style poll results to participant_data
#    participant_data:{'question1':[answer(s)],'question2':'no-data','question3':'answer-text'}
#
# Saves 'Response ID' as participant_id
#
# Will also detect participant links from the 'Participants' page and find more pages of participant links
#    participant_links:[hrefs] and participant_pages:[hrefs]
#
# Ex usage: parser = PDParser(survey_num=opt_dict['-s'].strip('='))
#           parser.feed(html_str)
#           print parser.participant_id
#           print parser.participant_data
#           print parser.participant_links
#           print parser.participant_pages
#           parser.reset_parser() #to remove the previous feed results
#
# Use view_type to limit participant page results to one of those in class variable VIEW_TYPES
#
##
import re
from HTMLParser import HTMLParser

class PDParser(HTMLParser):

    PARTICIPANT_LINK = re.compile('/surveys/\d+/report/\d+\?view_type')
    PARTICIPANT_LINK_PAGE = re.compile('/surveys/\d+/report/participants\?paged')

    VIEW_TYPES = ['all','incomplete','complete','locked']

    def __init__(self, survey_num, view_type='all', debug=False ):
        HTMLParser.__init__(self)
        if view_type not in self.VIEW_TYPES:
            raise(Exception('view type not recognized: %s'%view_type))

        self.debug      = debug
        self.survey_num = survey_num
        self.viewtype   = 'view_type='+view_type

        self.reset_parser()

    def reset_parser(self):
        self._enable_data = False  #enable data between nearby start and end tags.  Other data is usually empty.
        self._tag_level   = ''     #used to format debug statements
        self._state       = None   #the current state determined from relevant html 'class' types
        self._question    = None   #the current state's relevant question

        self.participant_links = {}
        self.participant_pages = []
        self.participant_data  = {}
        self.participant_id    = None

    def handle_starttag(self, tag, attrs):
        self._debug_print("Start tag:"+str(tag))

        self._enable_data = True

        for attr in attrs:

            if attr[0] == 'href':
                if self.PARTICIPANT_LINK.match(attr[1]):
                    participant_link = attr[1].split('view_type')[0]
                    if participant_link not in self.participant_links:
                        self.participant_links[participant_link] = {}

                if self.PARTICIPANT_LINK_PAGE.match(attr[1]):
                    participant_page = attr[1].split('view_type')[0]
                    if participant_page not in self.participant_pages:
                        self.participant_pages.append(participant_page)

            if attr[0] == 'class':
                if attr[1] in ['question',
                               'multiple-choice',
                               'multiple-choice-on',
                               'answer-text',
                               'rank-report',
                               'no-data',
                               'respondent-details']:
                    self._state=attr[1]

            self._debug_print("     attr:"+str(attr))

        self._tag_level+=' '

    def handle_endtag(self, tag):
        self._enable_data = False

        if self._state in ['multiple-choice-on','multiple-choice','rank-report'] and tag == 'table':
            self._reset_state()

        self._tag_level = self._tag_level[:-1]
        self._debug_print("End tag  :%s"%(tag))

    def handle_data(self, data):
        data = data.strip()
        if self._enable_data and data != '' and self._state != None:

            if self._state == 'question':
                self.participant_data[data] = None
                self._question = data
                self._state = None

            elif self._state == 'answer-text':
                self.participant_data[self._question] = data
                self._reset_state()

            elif self._state == 'no-data':
                self.participant_data[self._question] = 'no-data'
                self._reset_state()

            elif self._state == 'rank-report':
                if not data.isdigit(): #rank report results are numerated, don't add this integer valid data to the rank report
                    if self.participant_data[self._question] == None:
                        self.participant_data[self._question] = []
                    self.participant_data[self._question].append(data)

            elif self._state == 'multiple-choice-on':
                if self.participant_data[self._question] == None:
                    self.participant_data[self._question] = []
                self.participant_data[self._question].append(data)

            elif self._state == 'id':
                self.participant_id = data
                self._reset_state()

            elif self._state == 'respondent-details':
                if data == 'Response ID':
                    self._question = data
                    self._state = 'id'

            self._debug_print("Enabled Data      :"+str(data))
            return None

        self._debug_print("Disabled Data     :"+str(data))

    def _reset_state(self):
        self._state = None
        self._question = None

    def _debug_print(self,text):
        if self.debug:
            print self._tag_level+text
