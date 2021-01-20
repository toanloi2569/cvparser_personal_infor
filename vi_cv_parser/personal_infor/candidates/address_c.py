# import os 
# os.chdir(os.path.dirname(os.path.dirname(__file__)))

from fonduer.candidates.models import mention_subclass, candidate_subclass
from fonduer.candidates import CandidateExtractor
from fonduer.candidates.candidates import CandidateExtractorUDF
from vi_cv_parser.personal_infor.mentions.address import address_extract, address_extract_server
from fonduer.features import Featurizer
import vi_cv_parser.config as config

PARALLEL = config.PARALLEL # assuming a quad-core machine

def throttler(c):
    (address_c,) = c
    if address_c.context.sentence.page[0] != 1:
        return False 
    return True
    
class AddressExtract:
    def __init__(self, session):
        self.session = session
        self.Address = mention_subclass("Address")
        self.Address_C = candidate_subclass("Address_C", [self.Address])

    def get_throttler(self):
        return [throttler]

    def extract_mention(self, docs, parallelism=PARALLEL, clear=True):
        address_extract(docs, self.session, self.Address, PARALLEL, clear=clear)
        return self.Address

    def filter_candidate(self, docs, parallelism=PARALLEL, clear=True):
        candidate_extractor = CandidateExtractor(
            session=self.session, 
            candidate_classes=[self.Address_C], 
            throttlers=[throttler], 
            parallelism=parallelism
        )
        candidate_extractor.apply(docs, parallelism=parallelism, clear=clear)
        return self.Address_C, candidate_extractor.get_candidates()

class AddressExtractServer:
    def __init__(self):
        self.Address = mention_subclass("Address")
        self.Address_C = candidate_subclass("Address_C", [self.Address])

    def get_throttler(self):
        return [throttler]

    def extract_mention(self, document):
        document = address_extract_server(document, self.Address)
        return document

    def filter_candidate(self, document):
        document = CandidateExtractorUDF(
            [self.Address_C], 
            throttlers=self.get_throttler(), 
            self_relations = False, 
            nested_relations= False, 
            symmetric_relations = False
        ).apply(document, split=0)
    
        return document