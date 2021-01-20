from vi_cv_parser.handle.utils import *

def education_to_json(result,true_school_cpa, true_school_major,true_school_studytime):
    edus = {}
    for doc in result:
        edus[doc] = []
    # duyệt qua trường học và chuyên nghành
    for c in true_school_major:
        flag = False
        for edu in edus[c.school.context.sentence.document.name] :
            if edu.merge_university_major(c) == True:
                flag = True
                break
        if flag == False :
            education_item = education()
            education_item.set_university_major(c)
            edus[c.school.context.sentence.document.name].append(education_item)
    # duyệt qua trường học và thời gian
    for c in true_school_studytime:
        flag = False
        for edu in edus[c.school.context.sentence.document.name] :
            if edu.merge_university_time(c) == True:
                flag = True
                break
        if flag == False :
            education_item = education()
            education_item.set_university_time(c)
            edus[c.school.context.sentence.document.name].append(education_item)
    # duyệt qua trường học và cpa
    # for c in true_school_cpa:
    #     for edu in edus[c.school.context.sentence.document.name] :
    #         if edu.merge_university_cpa(c) == True:
    #             break

    for c in true_school_cpa:
        flag = False
        for edu in edus[c.school.context.sentence.document.name] :
            if edu.merge_university_cpa(c) == True:
                flag = True
                break
        if flag == False :
            education_item = education()
            education_item.set_university_cpa(c)
            edus[c.school.context.sentence.document.name].append(education_item)
    ## đưa dữ liệu vừa lấy được ở exps vào result
    ## đưa dữ liệu vừa lấy được ở exps vào result
    for doc in result:
        result[doc]["education"] = [edu.get_json() for edu in edus[doc]]
        
            
    return result

## mỗi đối tượng experience sẽ đại diện cho 1 bộ ba gồm công ty, vị trí và thời gian
class education :
    def __init__(self):
        self.university = {
            "id" : 0,
            "page": -1,
            "text": "",
            "box" : [],
            "html_attrs" : "",
            "id_overlap" : 0,  # nếu 1 tên Trường gồm 2 câu thì 1 câu sẽ vào overlab của câu còn lại
        }
        self.time = {
            "id" : 0,
            "text": "",
            "box" : [],
        }
        self.major = {
            "id" : 0,
            "text": "",
            "box" : [],
        }
        self.cpa = {
            "id" : 0,
            "text": "",
            "box" : [],
        }
    def get_json(self):
        return {
            "university": self.university["text"],
            "box_university": self.university["box"],
            "page": self.university["page"],
            "time": self.time["text"],
            "box_time": self.time["box"],
            "major": self.major["text"],
            "box_major": self.major["box"],
            "cpa": self.cpa["text"],
            "box_cpa": self.cpa["box"]
        }
    def set_university_major(self,university_major):
        self.university["id"] = university_major.school.context.sentence.position
        self.university["text"] = university_major.school.context.get_span()
        self.university["box"] = get_box(university_major.school)
        self.university["page"] = most_frequent(university_major.school.context.sentence.page)
        self.university["html_attrs"] = get_html(university_major.school)
        
        self.major["id"] = university_major.major.context.sentence.position
        self.major["text"] = university_major.major.context.get_span()
        self.major["box"] = get_box(university_major.major)
        
    def set_university_time(self,university_time):
        self.university["id"] = university_time.school.context.sentence.position
        self.university["text"] = university_time.school.context.get_span()
        self.university["box"] = get_box(university_time.school)
        self.university["page"] = most_frequent(university_time.school.context.sentence.page)
        self.university["html_attrs"] = get_html(university_time.school)
        
        self.time["id"] = university_time.study_time.context.sentence.position
        self.time["text"] = university_time.study_time.context.get_span()
        self.time["box"] = get_box(university_time.study_time)

    def set_university_cpa(self,university_cpa):
        self.university["id"] = university_cpa.school.context.sentence.position
        self.university["text"] = university_cpa.school.context.get_span()
        self.university["box"] = get_box(university_cpa.school)
        self.university["page"] = most_frequent(university_cpa.school.context.sentence.page)
        self.university["html_attrs"] = get_html(university_cpa.school)
        
        self.cpa["id"] = university_cpa.cpa.context.sentence.position
        self.cpa["text"] = university_cpa.cpa.context.get_span()
        self.cpa["box"] = get_box(university_cpa.cpa)
    
    # hàm trả về True với các trường hợp đã ghép xong và các trường hợp lặp, không cần ghép nữa
    # hàm trả về False với các trường hợp chưa có đối tượng education tương ứng
    def merge_university_major(self,university_major):
        if university_major.school.context.sentence.position != self.university["id"]:
            if self.university["id_overlap"] == 0:
                box1 = self.university["box"]
                box2 = get_box(university_major.school)
                if (get_html(university_major.school) == self.university["html_attrs"]) and vert_distance(box1,box2) < 10:
                    self.university["id_overlap"] = university_major.school.context.sentence.position
                    self.university["text"] += " "
                    self.university["text"] += university_major.school.context.get_span()
                    self.university["box"] = sum_box(box1,box2)
                    return True
        else :
            if self.major["id"] == 0:
                self.major["id"] = university_major.major.context.sentence.position
                self.major["text"] = university_major.major.context.get_span()
                self.major["box"] = get_box(university_major.major)
                return True
            return True
        
        if university_major.school.context.sentence.position == self.university["id_overlap"]:
            return True
        
        return False
    
    def merge_university_time(self,university_time):
        if university_time.school.context.sentence.position != self.university["id"]:
            if self.university["id_overlap"] == 0:
                box1 = self.university["box"]
                box2 = get_box(university_time.school)
                if (get_html(university_time.school) == self.university["html_attrs"]) and \
                        vert_distance(box1,box2) < 10 and horizontal_distance(box1, box2) < 10:
                    self.university["id_overlap"] = university_time.school.context.sentence.position
                    self.university["text"] += " "
                    self.university["text"] += university_time.school.context.get_span()
                    self.university["box"] = sum_box(box1,box2)
                    return True
        else :
            if self.time["id"] == 0:
                self.time["id"] = university_time.study_time.context.sentence.position
                self.time["text"] = university_time.study_time.context.get_span()
                self.time["box"] = get_box(university_time.study_time)
                return True
            else :
                self.time["text"] += " - "
                self.time["text"] += university_time.study_time.context.get_span()
                box1 = self.time["box"]
                box2 = get_box(university_time.study_time)
                self.time["box"] = sum_box(box1,box2)
                return True
        
        if university_time.school.context.sentence.position == self.university["id_overlap"]:
            return True
        return False
    def merge_university_cpa(self,university_cpa):
        if university_cpa.school.context.sentence.position == self.university["id"]:
            if self.cpa["id"] == 0:
                self.cpa["id"] = university_cpa.cpa.context.sentence.position
                self.cpa["text"] = university_cpa.cpa.context.get_span()
                self.cpa["box"] = get_box(university_cpa.cpa)
                return True
            return True
        if university_cpa.school.context.sentence.position == self.university["id_overlap"]:
            return True
        return False
