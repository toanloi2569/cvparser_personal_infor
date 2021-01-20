# import os 
# os.chdir(os.path.dirname(os.path.dirname(__file__)))

from fonduer.candidates.models import mention_subclass, candidate_subclass
from fonduer.candidates import CandidateExtractor
from fonduer.candidates.candidates import CandidateExtractorUDF
from vi_cv_parser.personal_infor.mentions.birthday import birthday_extract, birthday_extract_server
from vi_cv_parser.utils import parse_size
import vi_cv_parser.config as config

PARALLEL = config.PARALLEL # assuming a quad-core machine

# Tìm h xuất hiện ít nhất
def find_height_frequency(doc):
    list_height = []
    for sent in doc.sentences:
        if max(sent.right) == 0:
            continue
        else:
            list_height.append(parse_size(sent.html_attrs[0]))
    return min(list_height, key=list_height.count), list_height.count(min(list_height, key=list_height.count))

def throttler(c):
    (birthday_c,) = c
    doc = birthday_c.context.sentence.document
    height, count = find_height_frequency(doc)
    if parse_size(birthday_c.context.sentence.html_attrs[0]) == height and count == 1:
        return 1
    for birthday in doc.birthdays:
        if parse_size(birthday.context.sentence.html_attrs[0]) == height and count == 1:
            return 0
        if birthday.context.sentence.top[0] < birthday_c.context.sentence.top[0]:
            return 0
    return 1


class BirthdayExtract():
    def __init__(self, session):
        self.session = session
        self.Birthday = mention_subclass("Birthday")
        self.Birthday_C = candidate_subclass("Birthday_C", [self.Birthday])  

    def get_throttler(self):
        return [throttler]  

    def extract_mention(self, docs, clear=True):
        birthday_extract(docs, self.session, self.Birthday, PARALLEL, clear=clear)
        return self.Birthday

    def filter_candidate(self, docs, parallelism = PARALLEL, clear = True):
        candidate_extractor = CandidateExtractor(
            session=self.session, 
            candidate_classes=[self.Birthday_C], 
            throttlers=[throttler], 
            parallelism=parallelism
        )
        candidate_extractor.apply(docs, parallelism=parallelism, clear=clear)
        return self.Birthday_C, candidate_extractor.get_candidates()

class BirthdayExtractServer():
    def __init__(self):
        self.Birthday = mention_subclass("Birthday")
        self.Birthday_C = candidate_subclass("Birthday_C", [self.Birthday])  

    def get_throttler(self):
        return [throttler]  

    def extract_mention(self, document):
        document = birthday_extract_server(document, self.Birthday)
        return document

    def filter_candidate(self, document):
        document = CandidateExtractorUDF(
            [self.Birthday_C], 
            throttlers=self.get_throttler(), 
            self_relations = False, 
            nested_relations= False, 
            symmetric_relations = False
        ).apply(document, split=0)
    
        return document