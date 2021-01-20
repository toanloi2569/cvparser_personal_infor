import pickle
import numpy as np

from emmental.data import EmmentalDataLoader
from emmental.modules.embedding_module import EmbeddingModule

from fonduer.learning.dataset import FonduerDataset
from fonduer.features import Featurizer
from fonduer.features import FeatureExtractor
from fonduer.features.featurizer import FeaturizerUDF
# from fonduer.utils.data_model_utils import *

from vi_cv_parser.personal_infor.candidates.email_c import EmailExtractServer
from vi_cv_parser.personal_infor.candidates.phone_c import PhoneExtractServer 
from vi_cv_parser.utils import *
import vi_cv_parser.config as config

MODEL_PATH = config.MODEL_PATH

class PersonalInfor:
    def __init__(self):
        
        self.email_extract = EmailExtractServer()
        self.phone_extract = PhoneExtractServer()

    def extract_candidates(self, document):
        # email
        document = self.email_extract.extract_mention(document)
        document = self.email_extract.filter_candidate(document)

        # # phone
        document = self.phone_extract.extract_mention(document)
        document = self.phone_extract.filter_candidate(document)

        return document