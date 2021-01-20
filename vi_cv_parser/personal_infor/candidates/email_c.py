# import os 
# os.chdir(os.path.dirname(os.path.dirname(__file__)))

from fonduer.candidates.models import mention_subclass, candidate_subclass
from fonduer.candidates import CandidateExtractor
from fonduer.candidates.candidates import CandidateExtractorUDF
from vi_cv_parser.personal_infor.mentions.email import email_extract, email_extract_server
import vi_cv_parser.config as config

PARALLEL = config.PARALLEL # assuming a quad-core machine

def throttler(c):
    (email_c,) = c
    if email_c.context.sentence.page[0] != 1:
        return False 
    return True

class EmailExtract():
    def __init__(self, session):
        self.session = session
        self.Email = mention_subclass("Email")
        self.Email_C = candidate_subclass("Email_C", [self.Email])

    def get_throttler(self):
        return [throttler]

    def extract_mention(self, docs, parallelism=PARALLEL, clear=True):
        email_extract(docs, self.session, self.Email, PARALLEL, clear=clear)
        return self.Email

    def filter_candidate(self, docs, parallelism = PARALLEL, clear=True):
        candidate_extractor = CandidateExtractor(
            session=self.session, 
            candidate_classes=[self.Email_C], 
            throttlers=[throttler], 
            parallelism=parallelism
        )
        candidate_extractor.apply(docs, parallelism=parallelism, clear=clear)
        return self.Email_C, candidate_extractor.get_candidates()

class EmailExtractServer():
    def __init__(self):
        self.Email = mention_subclass("Email")
        self.Email_C = candidate_subclass("Email_C", [self.Email])  

    def get_throttler(self):
        return [throttler]  

    def extract_mention(self, document):
        document = email_extract_server(document, self.Email)
        return document

    def filter_candidate(self, document):
        document = CandidateExtractorUDF(
            [self.Email_C], 
            throttlers=self.get_throttler(), 
            self_relations = False, 
            nested_relations= False, 
            symmetric_relations = False
        ).apply(document, split=0)
    
        return document