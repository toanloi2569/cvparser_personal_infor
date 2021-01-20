# from fonduer.learning import LogisticRegression
# from metal.label_model import LabelModel
import torch
import numpy as np
from scipy.sparse.csr import csr_matrix
import csv
import pickle

## hàm này các featurier key lên , tham số thứ nhất là đối tượng featurier, tham số thứ 2 là đường dẫn đến file chứa bộ key
def load_keys(path_keys):
    with open(path_keys, 'rb') as f:
        key_names = pickle.load(f)
    return key_names

def load_word_counter(path_word_counter):
    with open(path_word_counter, 'rb') as f:
        word_counter = pickle.load(f)
    return word_counter


## hàm này để lấy các kết quả dự đoán đúng do mô hình hồi quy logistic trả ra
def get_predict(disc_model,cands, F_x, b=0.5):
    score = disc_model.predict((cands[0], F_x[0]), b=b, pos_label = 2)
    if 2 in score:
        true_pred = [cands[0][_] for _ in np.nditer(np.where(score == 2))]
    else :
        return []
    return true_pred

## chuyển kết quả trả về thành mảng các đối tượng json tương ứng với các doc
## chuyển kết quả trả về thành mảng các đối tượng json tương ứng với các doc
def convert_data(result):
    data = []
    for doc in result:
        doc_json = {
            "name": doc,
            "boxes" : []
        }
        
        for info in result[doc]["infor"]:
            doc_json["boxes"].append({ 
                    "text" : result[doc]["infor"][info]["text"],
                    "coordinates" : result[doc]["infor"][info]["box"],
                    "page" : 1,
                    "type" : info
                })
        for i,exp in enumerate(result[doc]["experience"]) :
            doc_json["boxes"].append({
                "text": exp["time"],
                # "coordinates": exp["box_time"],
                "page": exp["page"],
                "type" : "company_time",
                "category" : "exp_"+str(i+1)
            })
            
            doc_json["boxes"].append({
                "text": exp["company"],
                # "coordinates": exp["box_company"],
                "page": exp["page"],
                "type" : "company",
                "category" : "exp_"+str(i+1)
            })
            
            doc_json["boxes"].append({
                "text": exp["position"],
                # "coordinates": exp["box_position"],
                "page": exp["page"],
                "type" : "position",
                "category" : "exp_"+str(i+1)
            })
            
        for i,edu in enumerate(result[doc]["education"]) :
            doc_json["boxes"].append({
                "text": edu["time"],
                # "coordinates": edu["box_time"],
                "page": edu["page"],
                "type" : "study_time",
                "category" : "edu_"+str(i+1)
            })
            
            doc_json["boxes"].append({
                "text": edu["university"],
                # "coordinates": edu["box_university"],
                "page": edu["page"],
                "type" : "university",
                "category" : "edu_"+str(i+1)
            })
            
            doc_json["boxes"].append({
                "text": edu["major"],
                # "coordinates": edu["box_major"],
                "page": edu["page"],
                "type" : "major",
                "category" : "edu_"+str(i+1)
            })
            
            doc_json["boxes"].append({
                "text": edu["cpa"],
                # "coordinates": edu["box_cpa"],
                "page": edu["page"],
                "type" : "cpa",
                "category" : "edu_"+str(i+1)
            })
        
        for i,skill in enumerate(result[doc]["skill"]) :
            doc_json["boxes"].append({
                "text": skill["text"],
                # "coordinates": skill["box"],
                "page": skill["page"],
                "type" : "skill",
                "category" : "skill_"+str(i+1)
            })

        data.append(doc_json)
        
    return data


# # Sửa các trường hợp tách sai do spacy 09/20 18 -> 09/2018
# def fix_space_datetime(text):
#     text_ = text[0]
#     for k in range(1, len(text)-1):
#         if text[k] == ' ' and not text[k-1].isalpha() and not text[k+1].isalpha():
#             continue
#         text_ += text[k]
#     text_ += text[-1]
#     return text_


## hàm này để thay đổi kích thước của ma trận labeling cho phù hợp với gen_model
# Tham số thứ nhất là đối tượng gán nhãn Labeler
# Tham số thứ hai là ma trận thưa do Labeler sinh ra
# Tham số thứ ba là list các hàm gán nhãn
def resize_L_matrix(labeler,L_train,lbs):
    if len(labeler.get_keys()) == len(lbs):
        return L_train[0]
    key_model = [key.name for key in labeler.get_keys() ]
    key = [key.__name__ for key in lbs ] 
    L = np.array(L_train[0].toarray())
    for i,k in enumerate(key):
        if k not in key_model:
            L = np.insert(L,i,0,axis=1)
    L_csr_matrix = csr_matrix(L)
    return L_csr_matrix


# Lấy thuộc tính size của attribute
def parse_size(attrs):
    for attr in attrs.split():
        char_start = attr.find("size=")
        if char_start != -1:
            return float(attr[char_start+5:])


# Lấy thuộc tính font của attriute
def parse_font(attrs):
    for attr in attrs.split():
        char_start = attr.find("font=")
        if char_start != -1:
            return attr[char_start+5:]


def ismixed(text):
        return not text.islower() and not text.isupper()
    

# Lấy list các keys không cần thiết từ feature matrix và keys name
def get_keys_drop(F, keys,N=5):
    keys_drop = []
    blacklist = ['VIZ_e1_PAGE', 'VIZ_e2_PAGE', 'LEMMA', 'DDL_e1_W_POS_L', 'DDL_e2_W_POS_L', 
            'BASIC_e2_SPAN_TYPE', 'BASIC_e1_SPAN_TYPE', 'BASIC_e1_LENGTH', 'BASIC_e2_LENGTH']

    ## Lấy các key không cần thiết trong phân loại
    for key in keys:
        for bword in blacklist:
            if key.name.find(bword) != -1:
                keys_drop.append(key.name)

    start_word = len('BASIC_e1_CONTAINS_WORDS_[')
    end_word = -1
    for key in keys:
        key = key.name
        if key.find('BASIC_e1_CONTAINS_WORDS_[') != -1 or key.find('BASIC_e2_CONTAINS_WORDS_[') != -1:
            word = key[start_word:end_word]
            if len(word) == 1 and not word.isalpha():
                keys_drop.append(key)

    # Lấy các key có số lượng active quá ít
    matrix = F[0].transpose()
    counter = []
    for i in range(matrix.shape[0]):
        counter.append(matrix[i].count_nonzero())

    for key, count in zip(keys, counter):
        if count < N:
            keys_drop.append(key.name)

    return keys_drop


def get_feature_vector(keys, feature):
    F = [0 for _ in keys]
    for (k, v) in zip(feature['keys'], feature['values']):
        try:
            idx = keys.index(k)
            F[idx] = v
        except:
            continue
    return F

# Lấy vector feature của nhiều candidate cùng 1 lúc
# Đưa ra ma trận thưa biểu thị feature vector tương ứng với các candidate
def get_feature_vectors(key_names, features):
    F = []
    for f in features[0]:
        F.append(get_feature_vector(key_names, f))

    F = np.array(F)
    F = csr_matrix(F)
    return F