# import os 
# os.chdir(os.path.dirname(os.path.dirname(__file__)))

from fonduer.candidates.models import mention_subclass, candidate_subclass
from fonduer.candidates import CandidateExtractor
from fonduer.candidates.candidates import CandidateExtractorUDF
from vi_cv_parser.personal_infor.mentions.phone import phone_extract, phone_extract_server
import vi_cv_parser.config as config

PARALLEL = config.PARALLEL # assuming a quad-core machine

def throttler(c):
    (phone_c,) = c
    if phone_c.context.sentence.page[0] != 1:
        return False 
    doc = phone_c.context.sentence.document
    for phone in doc.phones:
        if phone.context.sentence.top[0] < phone_c.context.sentence.top[0]:
            return False
    return True

class PhoneExtract():
    def __init__(self, session):
        self.session = session
        self.Phone = mention_subclass("Phone")
        self.Phone_C = candidate_subclass("Phone_C", [self.Phone])

    def get_throttler(self):
        return [throttler]
    
    def extract_mention(self, docs, parallelism=PARALLEL, clear=True):
        phone_extract(docs, self.session, self.Phone, PARALLEL, clear=clear)
        return self.Phone

    def filter_candidate(self, docs, parallelism = PARALLEL, clear=True):
        candidate_extractor = CandidateExtractor(
            session=self.session, 
            candidate_classes=[self.Phone_C], 
            throttlers=[throttler], 
            parallelism=parallelism
        )
        candidate_extractor.apply(docs, parallelism=parallelism, clear=clear)
        return self.Phone_C, candidate_extractor.get_candidates()

class PhoneExtractServer():
    def __init__(self):
        self.Phone = mention_subclass("Phone")
        self.Phone_C = candidate_subclass("Phone_C", [self.Phone])

    def get_throttler(self):
        return [throttler]
    
    def extract_mention(self, document):
        document = phone_extract_server(document, self.Phone)
        return document

    def filter_candidate(self, document):
        document = CandidateExtractorUDF(
            [self.Phone_C], 
            throttlers=self.get_throttler(), 
            self_relations = False, 
            nested_relations= False, 
            symmetric_relations = False
        ).apply(document, split=0)
    
        return document