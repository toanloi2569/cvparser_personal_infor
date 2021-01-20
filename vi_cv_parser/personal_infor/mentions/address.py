# import os 
# os.chdir(os.path.dirname(os.path.dirname(__file__)))

from fonduer.candidates.models.implicit_span_mention import TemporaryImplicitSpanMention, TemporarySpanMention
from fonduer.candidates.mentions import MentionSentences, MentionNgrams
from fonduer.candidates.matchers import RegexMatchSpan,RegexMatchEach, DictionaryMatch, LambdaFunctionMatcher, Intersect, Union
from fonduer.utils.data_model_utils import *
from fonduer.candidates.models import Mention, mention_subclass
from fonduer.candidates import MentionExtractor
from fonduer.candidates.mentions import MentionExtractorUDF

''' MATCHER '''
def clean_word (word):
    bg = 0
    en = len(word)-1
    while bg < en and not word[bg].isalpha() and not word[bg].isdigit(): bg += 1
    while bg < en and not word[en].isalpha() and not word[en].isdigit(): en -= 1
    return word[bg:en+1]

# Address information often includes information about the province 
provinces = []
with open("cv_parser/personal_infor/mentions/data/province.txt", "r") as f:
    provinces = f.read()
provinces = provinces.splitlines()
def has_province_address(mention):
    text = mention.get_span().lower().replace('_', ' ')
    for province in provinces:
        if text.find(province) != -1:
            return True
    return False

# Address information often includes some geographics term such as "xã", "tỉnh" ... 
geographics_term = ["nhà", "ấp", "huyện", "tỉnh", "phố", "phường", "quận", \
                    "đường", "ngách", "ngõ", "city", "district", "street"]
def has_geographic_term_address(mention):
    text = mention.get_span().lower().replace('_', ' ')
    words = [word for word in text.split()]
    return any([True for term in geographics_term if term in words])

# Address information often have word "address" of "địa chỉ" in front
def address_prefix(mention):
    text = mention.get_span().lower().replace('_', ' ')
    return text.find('address') != -1 or text.find('địa chỉ') != -1
        
# Address information is usually a collection of 
# numbers, provinces' names (initial capital) and geographical terms.
# Those word should account for more than three-quater of the words in the sentences
def is_collection_of_number_and_geographical_term_and_provinces_name_address(mention):
    text = mention.get_span().replace('_', ' ')
    if text.find(':') != -1 :
        text = text[text.find(':'):]
    span = ''.join(e for e in text if e.isalnum() or e == ' ')
    words = span.split()
    term = ["nhà", "ấp", "huyện", "tỉnh", "thành", "phố", "thị", "phường", "quận", \
            "đường", "ngách", "ngõ", "city", "district", "street"]
    w = [1 for word in words if word[0].isdigit() or word[0].isupper() or clean_word(word).lower() in term]
    return sum(w) > 3*len(words)/4

# Address information often doesn't include some word "university", "college" ...
ignor_words = ["đại học", "cao đẳng", "công ty", "university", "college", "company"]
def hasnt_ignor_words(mention):
    text = mention.get_span().lower().replace('_', ' ')
    for igword in ignor_words:
        if text.find(igword) != -1:
            return False
    return True

def address_extract(docs, session, address_subclass, parallelism, clear=True):
    address_m1 = LambdaFunctionMatcher(func = has_province_address)
    address_m2 = LambdaFunctionMatcher(func = has_geographic_term_address)
    address_m3 = LambdaFunctionMatcher(func = address_prefix)
    address_m4 = LambdaFunctionMatcher(func = is_collection_of_number_and_geographical_term_and_provinces_name_address)
    address_m5 = LambdaFunctionMatcher(func = hasnt_ignor_words)
    address_matcher = Intersect(Union(address_m1, address_m2, address_m3), address_m4, address_m5)

    address_space = MentionSentences()
    
    mention_extractor = MentionExtractor(session, [address_subclass], [address_space], [address_matcher])
    mention_extractor.apply(docs, parallelism=parallelism,clear=clear)


def address_extract_server(document, address_subclass):
    address_m1 = LambdaFunctionMatcher(func = has_province_address)
    address_m2 = LambdaFunctionMatcher(func = has_geographic_term_address)
    address_m3 = LambdaFunctionMatcher(func = address_prefix)
    address_m4 = LambdaFunctionMatcher(func = is_collection_of_number_and_geographical_term_and_provinces_name_address)
    address_m5 = LambdaFunctionMatcher(func = hasnt_ignor_words)
    address_matcher = Intersect(Union(address_m1, address_m2, address_m3), address_m4, address_m5)

    address_space = MentionSentences()
    
    document = MentionExtractorUDF([address_subclass], [address_space], [address_matcher]).apply(document)
    return document