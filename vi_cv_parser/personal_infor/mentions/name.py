import csv
from fonduer.candidates.models import mention_subclass
from fonduer.candidates.matchers import RegexMatchSpan,RegexMatchEach, DictionaryMatch, LambdaFunctionMatcher, Intersect, Union
from fonduer.utils.data_model_utils import *
from fonduer.candidates.mentions import MentionSpace, MentionSentences
from fonduer.candidates.models.span_mention import TemporarySpanMention
from fonduer.candidates import MentionExtractor
from fonduer.candidates.mentions import MentionExtractorUDF
import re 

class MentionName(MentionSentences):

    def apply(self, doc):

        for sentence in doc.sentences:
            text = sentence.text.lower().replace('_',' ')
            prefixes = ['họ tên', 'họ và tên']
            check = True

            for prefix in prefixes:
                start = text.find(prefix)
                if start != -1 :
                    # Trường hợp câu chứa tiền tố là "họ tên" nhưng bị tách làm 2
                    if start + len(prefix) + 5 >= len(text):
                        check = False
                        continue
                    # Trường hợp "họ tên : ABCxyz"
                    elif text.find(': ') != -1:
                        start = text.find(': ') + 2
                    else:
                        start += len(prefix)+1
                    
                    check = False 
                    yield TemporarySpanMention(
                        char_start=start, char_end=len(text)-1, sentence=sentence
                    )
            
            if check:
                yield TemporarySpanMention(
                    char_start=0, char_end=len(text)-1, sentence=sentence
                )

last_name_vn = []
# Đọc file lấy tên phổ biến bằng tiếng anh
with open ("cv_parser/personal_infor/mentions/data/lastname.txt", "r") as file:
    reader = csv.reader(file)
    for line in reader:
        part = line
        last_name_vn.append(part[0])

list_name_common = []
# Đọc file lấy tên phổ biến bằng tiếng anh
with open ("cv_parser/personal_infor/mentions/data/name_common.txt", "r") as file: 
    reader = csv.reader(file)
    for line in reader:
        part = line
        list_name_common.append(part[0])

# Tên lớn hơn 6 và nhỏ hơn 2 thì loại
def length_name(mention):
    name = mention.get_span().replace('_', ' ')
    list_ele_name = name.split()
    if len(list_ele_name) > 6 or len(list_ele_name) < 2:
        return 0
    return 1

# Tên nằm ở trang 2 trở lên hoặc ở nửa dưới của trang thì loại
def position_name(mention):
    name = mention.get_span().replace('_', ' ')
    list_ele_name = name.split()
    if mention.sentence.top[0] > 300 or mention.sentence.page[0] != 1 or max(mention.sentence.right) == 0:
        return 0
    return 1

# Tên không được viết hoa bộ hoặc viết hoa đầu mỗi từ thì loại
def capitalize_name(mention):
    name = mention.get_span().replace('_', ' ')
    list_ele_name = name.split()
    for ele_name in list_ele_name:
        if ele_name != ele_name.capitalize() and ele_name != ele_name.upper():
            return 0
    return 1

# Phần từ đầu cầu bằng họ thì trả về true
def last_name(mention):
    name = mention.get_span().replace('_', ' ')
    list_ele_name = name.split()
    if len(list_ele_name) < 2:
        return 0
    for last_name in last_name_vn:
        if last_name == list_ele_name[0].lower() or last_name == list_ele_name[1].lower():
            return 1
    return 0

# Áp dụng cho tiếng anh với tên phổ biến ở phần tử đầu tiên
def name_common(mention):
    name = mention.get_span().replace('_',' ')
    list_ele_name = name.split()
    for name_common in list_name_common:
        if name_common == list_ele_name[0].lower() or name_common == list_ele_name[-1].lower() :
            return 1
    return 0

def check_name(mention):
    name = mention.get_span().lower().replace('_',' ')
    list_digit = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    list_symbol = ["+", "/", "\\", "@", "$", "%", "^", "*", ";"]
    list_expel = ["cao đẳng","công ty","trung cấp","trưởng phòng","tuyển dụng","tổ hợp","quản lý",
                 "cửa hàng","trà sữa","trung học","giao viên", "hình ảnh","trình độ","truyền thông",
                 "shop","chuyên môn","kỹ năng","hà nội","mục tiêu","việt nam","kỹ sư","học viên","học viện",
                 "hoạt động","sinh viên","cử nhân", "học vấn","đại học","thông tin","da nang", "dự án",
                 "company","java", "an toàn thông tin", "tranning", "document", "school", "college", 
                 "mong muốn", "kiến thức", "dữ liệu", "web", "trường đại học", "university", "street", 
                 "lập trình", "chi tiết", "dự tuyển", "ứng tuyển", "trung tâm", "công nghệ", "thực tập",
                 "city", "nhân viên", "nghề nghiệp","quản trị","thường tín","thành phố","phát triển",
                 "giao dịch","quốc tế","chuyên viên","kiểm toán","tổng hợp","đại học","đh","cđ","cao dang",
                 "dai hoc","cong ty","thpt","tốt nghiệp","thcs","làm việc","quá trình","lý lịch", 
                 "tổng quan", "hồ sơ", "xin việc", "ký", "ghi", "ngày sinh", "năm sinh", "ngày tháng", 
                 "điện thoại", "email", "địa chỉ", "giới tính"]
    list_remove = list_digit + list_symbol + list_expel
    for i in list_remove:
        if name.find(i)!= -1:
            return 0
    if name.find('và') != -1 and name.find('tên') == -1:
        return 0
    return 1

def prefix_name(mention):
    name = mention.get_span().lower().replace('_', ' ')
    prefixes = ['họ tên', 'họ và tên']
    for i in prefixes:
        if name.find(i) != -1:
            return 1
    return 0
    

def name_extract(docs, session, name_subclass, parallelism, clear=True):
    length_name_matcher = LambdaFunctionMatcher(func=length_name)
    position_name_matcher = LambdaFunctionMatcher(func=position_name)
    capitalize_name_matcher = LambdaFunctionMatcher(func=capitalize_name)

    last_name_matcher = LambdaFunctionMatcher(func=last_name)
    name_common_matcher = LambdaFunctionMatcher(func=name_common)
    check_name_matcher = LambdaFunctionMatcher(func = check_name)
    prefix_name_matcher = LambdaFunctionMatcher(func=prefix_name)

    form_name_matcher = Intersect(length_name_matcher, position_name_matcher, capitalize_name_matcher)
    name_matcher = Intersect(
        Union(
            Intersect(last_name_matcher, form_name_matcher),
            Intersect(name_common_matcher, form_name_matcher),
            prefix_name_matcher
        ),
        check_name_matcher
    )
    name_space = MentionName()

    mention_extractor = MentionExtractor(session, [name_subclass], [name_space], [name_matcher])
    mention_extractor.apply(docs, parallelism=parallelism,clear=clear)

def name_extract_server(document, name_subclass):
    length_name_matcher = LambdaFunctionMatcher(func=length_name)
    position_name_matcher = LambdaFunctionMatcher(func=position_name)
    capitalize_name_matcher = LambdaFunctionMatcher(func=capitalize_name)

    last_name_matcher = LambdaFunctionMatcher(func=last_name)
    name_common_matcher = LambdaFunctionMatcher(func=name_common)
    check_name_matcher = LambdaFunctionMatcher(func = check_name)
    prefix_name_matcher = LambdaFunctionMatcher(func=prefix_name)

    form_name_matcher = Intersect(length_name_matcher, position_name_matcher, capitalize_name_matcher)
    name_matcher = Intersect(
        Union(
            Intersect(last_name_matcher, form_name_matcher),
            Intersect(name_common_matcher, form_name_matcher),
            prefix_name_matcher
        ),
        check_name_matcher
    )

    name_space = MentionName()

    document = MentionExtractorUDF([name_subclass], [name_space], [name_matcher]).apply(document)
    return document