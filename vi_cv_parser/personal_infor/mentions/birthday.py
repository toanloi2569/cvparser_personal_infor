from fonduer.candidates.mentions import MentionSpace
from fonduer.candidates.models.span_mention import TemporarySpanMention
from fonduer.parser.models import Document, Sentence
from fonduer.candidates.matchers import RegexMatchSpan,RegexMatchEach, DictionaryMatch, LambdaFunctionMatcher, Intersect, Union
from fonduer.utils.data_model_utils import *
from fonduer.candidates.models import Mention, mention_subclass
from fonduer.candidates import MentionExtractor
from fonduer.candidates.mentions import MentionExtractorUDF
import re


    

flags = re.IGNORECASE|re.MULTILINE|re.UNICODE


def generate_patterns():
    from datetime import date
    patterns = {}

    days_of_the_month_as_numbers = list(map(str, list(reversed(range(1,32))))) + list(map(lambda n : u"0"+str(n),range(0, 10))) 
    __ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
    days_of_the_month_as_ordinal = [__ordinal(n) for n in range(1,32)]
    months_verbose = ["January","Febuary","February","March","April","May","June","July","August","September","October","November","December"]
    months_abbreviated = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"] 
    months_as_numbers = list(map(str,range(1,13))) + list(map(lambda n : u"0"+str(n),range(0, 10))) 

    current_year = date.today().year
    _years_as_numbers = range(1900, current_year+200)
    _years_as_strings = list(map(str,_years_as_numbers))
    years = _years_as_strings + [y[-2:] for y in _years_as_strings]
    months_last_three_letters = [month[-3:] if len(month[-3:]) == 3 else " " + month[-2:] for month in months_verbose]


    patterns['days_of_the_month_as_numbers'] = "(?:" + "|".join(days_of_the_month_as_numbers) + ")"
    patterns['days_of_the_month_as_ordinal'] = "(?:" + "|".join(days_of_the_month_as_ordinal) + ")"
    patterns['months_verbose'] = "(?:" + "|".join(months_verbose) + ")"
    patterns['months_abbreviated'] = "(?:" + "|".join(months_abbreviated) + ")"
    patterns['months_as_numbers'] = "(?:" + "|".join(months_as_numbers) + ")"
    patterns['years'] = "(?:" + "|".join(years) + ")"
    patterns['months_last_three_letters'] = "(?:" + "|".join(months_last_three_letters) + ")"
    #merge months as regular name, abbreviation and number all together
    patterns['day'] = u'(?P<day>' + patterns['days_of_the_month_as_numbers'] + u'|' + patterns['days_of_the_month_as_ordinal'] + ')(?!\d{2,4})'

    #merge months as regular name, abbreviation and number all together
    # makes sure that it doesn't pull out 3 as the month in January 23, 2015
    patterns['month'] = u'(?<! \d)(?P<month>' + patterns['months_verbose'] + u'|' + patterns['months_abbreviated'] + u'|' + patterns['months_as_numbers'] + u')' + u"(?:" + "/" + patterns['months_verbose'] + u")?" + u"(?!\d-\d{1,2}T)"

    # spaces or punctuation separatings days, months and years
    # blank space, comma, dash, period, backslash
    # todo: write code for forward slash, an escape character
    #patterns['punctuation'] = u"(?P<punctuation>, |:| |,|-|\.|\/|)"
    patterns['punctuation'] = u"(?:, |:| |,|-|\.|\/)"
    patterns['punctuation_fixed_width'] = u"(?: |,|;|-|\.|\/)"
    patterns['punctuation_nocomma'] = u"(?: |-|\.|\/)"
    #patterns['punctuation_second'] = u"\g<punctuation>"
    patterns['punctuation_second'] = patterns['punctuation']

    # matches the year as two digits or four
    # tried to match the four digits first
    # (?!, \d{2,4}) makes sure it doesn't pick out 23 as the year in January 23, 2015
    patterns['year'] = u"(?P<year>" + patterns['years'] + u")" + "(?!th)"

    patterns['dmy'] = u"(?<!\d{2}:)" + u"(?<!\d)" + u"(?P<dmy>" + patterns['day'].replace("day", "day_dmy") + patterns['punctuation'].replace("punctuation","punctuation_dmy") + patterns['month'].replace("month","month_dmy") + patterns['punctuation_second'].replace("punctuation","punctuation_dmy") + patterns['year'].replace("year", "year_dmy") + u")" 

    patterns['mdy'] =  u"(?!\d{2}:)" + u"(?<!\d{3})" + u"(?P<mdy>" + patterns['month'].replace("month", "month_mdy") + patterns['punctuation'].replace("punctuation","punctuation_mdy") + patterns['day'].replace("day","day_mdy") + "(?:" + patterns['punctuation_second'].replace("punctuation","punctuation_mdy") + "|, )" + patterns['year'].replace("mdy","year_mdy") + u")" 


    #we don't include T in the exclusion at end because sometimes T comes before hours and minutes
    patterns['ymd'] = u"(?<![\dA-Za-z])" + u"(?P<ymd>" + patterns['year'].replace("year","year_ymd") + patterns['punctuation'].replace("punctuation","punctuation_ymd") + patterns['month'].replace("month","month_ymd") + patterns['punctuation_second'].replace("punctuation","punctuation_ymd") + patterns['day'].replace("day","day_ymd") + u")" + "(?<![^\d]\d{4})" + u"(?!-\d{1,2}-\d{1,2})(?![\dABCDEFGHIJKLMNOPQRSUVWXYZabcdefghijklmnopqrsuvwxyz])"

    patterns['my'] = u"(?<!\d{3})" + u"(?<!32 )" + u"(?P<my>" + patterns['month'].replace("month","month_my") + patterns['punctuation_nocomma'] + patterns['year'].replace("year","year_my") + u")"

    # just the year
    # avoiding 32 december 2017
    patterns['y'] = u"(?<!\d{2}:)" + "(?<!\d)" + "(?<!" + patterns['months_last_three_letters'] + patterns['punctuation_fixed_width'] + ")" +  u"(?P<y>" + patterns['year'].replace("year","year_y") + u")" + "(?!" + patterns['punctuation_fixed_width'] + patterns['months_abbreviated'] + ")" + u"(?!\d)" + u"(?!:\d{2})"
    patterns['date'] = date = u"(?P<date>" + patterns['mdy'] + "|" + patterns['dmy'] + "|" + patterns['ymd'] + "|" + patterns['my'] + "|" + patterns['y'] + u")"

    patterns['date_compiled'] = re.compile(date, flags)   
    return patterns
    

class MentionDates(MentionSpace):
    """Defines the space of Mentions as date patterns in a Document *x*."""
    flags = re.IGNORECASE|re.MULTILINE|re.UNICODE
    patterns = generate_patterns()

    def __init__(self):
        """Initialize MentionSentences."""
        MentionSpace.__init__(self)
        
    # convert list to string
    def convert(list):      
        s = [str(i) for i in list]    
        # Join list items using join() 
        res = "".join(s)
        return(res) 
    
    # check the spacing to match number
    def checkSpaceNumber(text):
        arr = []
        arr_space = []
        list_text = list(text)
        for i in range(len(text)):
            if list_text[i].isnumeric() == True:
                arr.append(i)
        if len(arr) == 0: return [0,text]
        else:
            for i in range(min(arr)-1,max(arr)+1):
                if list_text[i] == " ":
                    arr_space.append(i)
            a = 0
            for i in arr_space:
                list_text.pop(i-a)
                a = a + 1 
            return [len(arr_space),MentionDates.convert(list_text)]
        
    def extract_dates(self, text):
        for match in re.finditer(re.compile(MentionDates.patterns['date'], flags), MentionDates.checkSpaceNumber(text)[1]):
            s = match.start()
            e = match.end() + MentionDates.checkSpaceNumber(text)[0]
            yield (s, e, text[s:e])    

    @staticmethod
    def parse_date(text):
        tmp = list(re.finditer(re.compile(MentionDates.patterns['date'], flags), text.replace(" ","")))
        if len(tmp) != 1: 
            return None 
        else:
            items = dict((k.split("_")[0], v) for k, v in tmp[0].groupdict().items() if v)
            return {k: v for k, v in items.items() if k in ('month', 'day', 'year')}
            
    def apply(self, doc):
        """
        Generate MentionSentences from a Document by parsing all of its Sentences.
        :param doc: The ``Document`` to parse.
        :type doc: ``Document``
        :raises TypeError: If the input doc is not of type ``Document``.
        """
        if not isinstance(doc, Document):
            raise TypeError(
                "Input Contexts to MentionSentences.apply() must be of type Document"
            )

        for sentence in doc.sentences:
            for date_mention in self.extract_dates(sentence.text):
                yield TemporarySpanMention(
                    char_start=date_mention[0], char_end=date_mention[1] - 1, sentence=sentence
                )


def birthday_conditions(attr):
    if attr.sentence.page[0] != 1 or max(attr.sentence.right) == 0:
        return 0
    tmp = MentionDates.parse_date(attr.get_span())
    if tmp and len(tmp) >= 3:
        return 1
    else:
        return 0

def filter_birthday(mention):
    text = mention.get_span()
    list_punctuation = [".",":","/","-"]
    #birthOfBirthDay is only number if count(number) < 9
    count_digit = 0
    count_alpha = 0
    for i in text:
        if text.isdigit():count_digit = count_digit + 1
        if text.isalpha(): count_alpha = count_alpha + 1
    for i in list_punctuation:
        if text.count(i) == 2:
            if count_digit <9 and len(text) < 18 and count_alpha <9:
                return 1

def birthday_extract(docs, session, birthday_subclass, parallelism, clear=True):
    filter_birthday_matcher = LambdaFunctionMatcher(func=filter_birthday, longest_match_only= True)
    birthday_conditions_matcher = LambdaFunctionMatcher(func=birthday_conditions, longest_match_only= True) 
    birthday_matcher = Intersect(filter_birthday_matcher,birthday_conditions_matcher)
    birthday_space = MentionDates()
    
    mention_extractor = MentionExtractor(session, [birthday_subclass], [birthday_space], [birthday_matcher])
    mention_extractor.apply(docs, parallelism=parallelism, clear=clear)

def birthday_extract_server(document, birthday_subclass):
    filter_birthday_matcher = LambdaFunctionMatcher(func=filter_birthday, longest_match_only= True)
    birthday_conditions_matcher = LambdaFunctionMatcher(func=birthday_conditions, longest_match_only= True) 
    birthday_matcher = Intersect(filter_birthday_matcher,birthday_conditions_matcher)
    birthday_space = MentionDates()
    
    document = MentionExtractorUDF([birthday_subclass], [birthday_space], [birthday_matcher]).apply(document)
    return document
