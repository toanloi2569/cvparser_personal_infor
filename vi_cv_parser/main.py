import pickle 
import time 
import logging

from fonduer import Meta, init_logging
from fonduer.parser.preprocessors import XMLDocPreprocessor
from fonduer.parser.parser_xml import Parser_xml, Parser_xmlUDF
from fonduer.parser.models import Document
from fonduer.candidates.models import mention_subclass, candidate_subclass

from vi_cv_parser.personal_infor.personal_infor import PersonalInfor
from vi_cv_parser.handle.handle import build_json
from vi_cv_parser.handle.handle_personal_infor import personal_infor_to_json

from vi_cv_parser.utils import *
import json

init_logging(log_dir="logs")
logging = logging.getLogger(__name__)

class CvParser:
    def __init__(self):
        self.document = None
        self.personal_infor = PersonalInfor()

    # Parser file pdf trong folder truyền vào
    def parse(self, folder_data):
        start = time.time()
        document = XMLDocPreprocessor(folder_data)._generate()
        document = document.__next__()
        corpus_parser = Parser_xmlUDF(structural=True, lingual=True, visual=True,  tabular=True,
                                        pdf_path=folder_data, language='vi', strip=False, flatten=["span", "br"],
                                        blacklist=["style", "script","layout","figure","text","textline"], 
                                        replacements=[("[\u2010\u2011\u2012\u2013\u2014\u2212]", "-")]
                                    )   
        
        document = corpus_parser.apply(document)
        end = time.time()
        logging.info(f'\tTime to parse {document.name} : {end - start}')
        return document

    # Extract document truyền vào, trả kết quản dạng json
    def extract_data(self, document):

        document, true_email, true_phone = self.extract_personal_info(document)

        ## xử lý kết quả trả về
        result = build_json([document])
        result = personal_infor_to_json(result, [], true_email, [], [], true_phone)

        return result

    def extract_personal_info(self, document):
        ### personal info
        start = time.time()
        true_email, true_phone = [], []

        # try :
        document = self.personal_infor.extract_candidates(document)

        if len(document.phone_cs) != 0:
            true_phone = document.phone_cs
        if len(document.email_cs) != 0:
            true_email = document.email_cs
      
        end = time.time()
        logging.info(f'\tTime to extract personal info from {document.name} : {end - start}')
        return document, true_email, true_phone

    # hàm này trả về kết quả dưới dạng đối tượng json có cấu trúc cây
    def get_result(self):
        return self.result
    # hàm này trả về kết quả dưới dạng một mảng các đối tượng json đại diện cho các CV
    def get_list_json(self, result):
        return convert_data(result)
    # hàm này lưu kết quả (ở dạng một mảng các đối tượng json) vào file
    def extract_file_json(self,file_name):
        with open(file_name, "w") as file_json:
            data = convert_data(self.result)
            json.dump(data,file_json)
            file_json.close()
    
    ## hàm này trả về các candidate được dự đoán đúng (có xác suất lớn hơn b)
    def get_true_personal_infor(self):
        return self.true_name, self.true_email, self.true_birthday, self.true_address ,self.true_phone
    ## hàm này trả về tất cả các candidate
    def get_cands_personal_infor(self):
        return self.name, self.email, self.birthday, self.address , self.phone
    ## hàm này trả về tất cả các xác suất dự đoán của tất cả candidate
    def get_marginals_personal_infor(self):
        return   self.marginals_name,self.marginals_email,self.marginals_birthday, self.marginals_address, self.marginals_phone
    
    def get_true_experience(self):
        return self.true_com_pos, self.true_com_dat

    def get_marginals_experience(self):
        return self.marginals_com_pos, self.marginals_com_dat

    def get_cands_experience(self):
        return self.cands_com_pos, self.cands_com_dat

    def get_true_education(self):
        return self.true_school_cpa, self.true_school_major, self.true_school_studytime

    def get_marginals_education(self):
        return self.marginals_school_cpa, self.marginals_school_major, self.marginals_school_studytime

    def get_cands_education(self):
        return self.cands_SchoolCpa_C,self.cands_SchoolMajor_C,self.cands_SchoolStudyTime_C
    
    def get_true_skill(self):
        return self.true_skill

    def get_marginals_skill(self):
        return self.marginals_skill

    def get_cands_skill(self):
        return self.cands_skill

    def drop_db(self):
        self.session.close()
        self.session.get_bind().dispose()
    
