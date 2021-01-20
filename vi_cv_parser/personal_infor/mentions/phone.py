import re
from fonduer.candidates import MentionSentences
from fonduer.candidates.models.span_mention import TemporarySpanMention
from fonduer.candidates.mentions import MentionSpace
from fonduer.candidates.matchers import RegexMatchEach, LambdaFunctionMatcher, Union
from fonduer.utils.data_model_utils import *
from fonduer.candidates import MentionExtractor
from fonduer.candidates.mentions import MentionExtractorUDF
from fonduer.parser.models import Document
    
class MentionPhoneNumber(MentionSentences):
#     def apply(self, doc):

#         list_digit = ['0','1','2','3','4','5','6','7','8','9']
#         symbol_plus = '+'
#         sympol_bracket = "(+"

#         start_rgx = r'(\d|\+|\(\+)'
#         number_phone = '([(]?\+84[)]?[ ]*\d{1,3}|0\d{2,4})[ ]?(-|\.)?[ ]?\d{3,4}[ ]?(-|\.)?[ ]?\d{3,4}'
#         for sentence in doc.sentences:
#             text = sentence.text

#             # Tìm vị trí bắt đầu của số điện thoại
#             match = re.search(start_rgx, text)
#             start = -1 if match is None else match.start()

#             # Tìm vị trí kết thúc của số điện thoại
#             end = -1
#             for i in range(len(text)-1, 0, -1):
#                 if text[i].isdigit() and re.search('[a-zA-Z]', text[start:i+1]) is None:
#                     end = i   
#                     break

#             if start != -1 and start < end: 
#                 yield TemporarySpanMention(
#                     char_start=start, char_end=end+1, sentence=sentence
#                 )   
                
    def apply(self, doc):

        list_digit = ['0','1','2','3','4','5','6','7','8','9']
        symbol_plus = '+'
        sympol_bracket = "(+"

        start_rgx = r'(\d|\+|\(\+)'
        number_phone = '([(]?\+84[)]?[ ]*\d{1,3}|0\d{2,4})[ ]?(-|\.)?[ ]?\d{3,4}[ ]?(-|\.)?[ ]?\d{3,4}'
        for sentence in doc.sentences:
            text = sentence.text
            matches = re.finditer(start_rgx, text)
            if matches is None:
                start = -1
            else:
                for match in matches:
                    start = match.start()
                    end = -1
                    for i in range(len(text)-1, 0, -1):
                        if text[i].isdigit() and re.search('[a-zA-Z]', text[start:i+1]) is None:
                            end = i   
                            break
                    if start != -1 and start < end: 
                        yield TemporarySpanMention(
                            char_start=start, char_end=end, sentence=sentence
                        )
            
def matcher_number_phone(mention):
    number_phone = mention.get_span()
    if "/" in number_phone or len(number_phone.split("-")) != 3:
        return False

    return 9 < len(re.sub(r'\+|-|\(|\)|\s', '', number_phone)) < 12

# regex
number_phone = '^([(]?\+84[)]?[ ]*\d{1,3}|0\d{2,4})[ ]?(-|\.)?[ ]?\d{3,4}[ ]?(-|\.)?[ ]?\d{3,4}$'
def regexMatch(mention):
    return re.search(number_phone,mention.get_span()) is not None 

def phone_extract(docs, session, phone_subclass, parallelism, clear=True):
    phone_lambda_matcher = LambdaFunctionMatcher(func=matcher_number_phone)
    regex_matcher = LambdaFunctionMatcher(func=regexMatch)
    phone_lamda_matcher = Union(regex_matcher, phone_lambda_matcher)

    phone_space = MentionPhoneNumber()
    
    mention_extractor = MentionExtractor(session, [phone_subclass], [phone_space], [phone_lamda_matcher])
    mention_extractor.apply(docs, parallelism=parallelism, clear=clear)

def phone_extract_server(document, phone_subclass):
    phone_lambda_matcher = LambdaFunctionMatcher(func=matcher_number_phone)
    regex_matcher = LambdaFunctionMatcher(func=regexMatch)
    phone_lamda_matcher = Union(regex_matcher, phone_lambda_matcher)

    phone_space = MentionPhoneNumber()
    
    document = MentionExtractorUDF([phone_subclass], [phone_space], [phone_lamda_matcher]).apply(document)
    return document
