# import os 
# os.chdir(os.path.dirname(os.path.dirname(__file__)))

from fonduer.candidates.models import mention_subclass, candidate_subclass
from fonduer.candidates import CandidateExtractor
from fonduer.candidates.candidates import CandidateExtractorUDF
from vi_cv_parser.personal_infor.mentions.name import name_extract, name_extract_server
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
    (name_c,) = c
    doc = name_c.context.sentence.document
    height, count = find_height_frequency(doc)
    if parse_size(name_c.context.sentence.html_attrs[0]) == height and count == 1:
        return 1
    for name in doc.names:
        if parse_size(name.context.sentence.html_attrs[0]) == height and count == 1:
            return 0
        if name.context.sentence.top[0] < name_c.context.sentence.top[0]:
            return 0
    return 1

class NameExtract():
    def __init__(self, session):
        self.session = session
        self.Name = mention_subclass("Name")
        self.Name_C = candidate_subclass("Name_C", [self.Name])

    def get_throttler(self):
        return [throttler]

    def extract_mention(self, docs, parallelism=PARALLEL, clear=True):
        name_extract(docs, self.session, self.Name, PARALLEL, clear=clear)
        return self.Name

    def filter_candidate(self, docs, parallelism = PARALLEL, clear=True):
        candidate_extractor = CandidateExtractor(
            session=self.session, 
            candidate_classes=[self.Name_C], 
            throttlers=[throttler], 
            parallelism=parallelism
        )
        candidate_extractor.apply(docs, parallelism=parallelism, clear=clear)
        return self.Name_C, candidate_extractor.get_candidates()

class NameExtractServer():
    def __init__(self):
        self.Name = mention_subclass("Name")
        self.Name_C = candidate_subclass("Name_C", [self.Name])

    def get_throttler(self):
        return [throttler]

    def extract_mention(self, document):
        document = name_extract_server(document, self.Name)
        return document

    def filter_candidate(self, document):
        document = CandidateExtractorUDF(
            [self.Name_C], 
            throttlers=self.get_throttler(), 
            self_relations = False, 
            nested_relations= False, 
            symmetric_relations = False
        ).apply(document, split=0)
    
        return document
        