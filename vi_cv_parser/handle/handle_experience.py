from vi_cv_parser.handle.utils import *

def experience_to_json(result,true_com_pos, true_com_dat):
    exps = {}
    for doc in result:
        exps[doc] = []
    for c_pos in true_com_pos:
        flag = False
        for exp in exps[c_pos.company.context.sentence.document.name] :
            if exp.merge_com_pos(c_pos) == True:
                flag = True
                break
        if flag == False :
            experience_item = experience()
            experience_item.set_com_pos(c_pos)
            exps[c_pos.company.context.sentence.document.name].append(experience_item)
            
    for c_dat in true_com_dat:
        flag = False
        for exp in exps[c_dat.company.context.sentence.document.name] :
            if exp.merge_com_dat(c_dat) == True:
                flag = True
                break
        if flag == False :
            experience_item = experience()
            experience_item.set_com_dat(c_dat)
            exps[c_dat.company.context.sentence.document.name].append(experience_item)
            
    ## đưa dữ liệu vừa lấy được ở exps vào result
    for doc in result:
        result[doc]["experience"] = [exp.get_json() for exp in exps[doc]]
        
            
    return result

## mỗi đối tượng experience sẽ đại diện cho 1 bộ ba gồm công ty, vị trí và thời gian
class experience :
    def __init__(self):
        self.company = {
            "id" : 0,
            "page": -1,
            "text": "",
            "box" : [],
            "html_attrs" : "",
            "id_overlap" : 0,  # nếu 1 tên công ty gồm 2 câu thì 1 câu sẽ vào overlab của câu còn lại
        }
        self.time = {
            "id" : 0,
            "text": "",
            "box" : [],
        }
        self.position = {
            "id" : 0,
            "text": "",
            "box" : [],
        }
        
    def get_json(self):
        return {
            "company": self.company["text"],
            "box_company": self.company["box"],
            "page": self.company["page"],
            "time": self.time["text"],
            "box_time": self.time["box"],
            "position": self.position["text"],
            "box_position": self.position["box"]
        }
    def set_com_pos(self,com_pos):
        self.company["id"] = com_pos.company.context.sentence.position
        self.company["text"] = com_pos.company.context.get_span()
        self.company["box"] = get_box(com_pos.company)
        self.company["page"] = most_frequent(com_pos.company.context.sentence.page)
        self.company["html_attrs"] = get_html(com_pos.company)
        
        self.position["id"] = com_pos.position.context.sentence.position
        self.position["text"] = com_pos.position.context.get_span()
        self.position["box"] = get_box(com_pos.position)
        
    def set_com_dat(self,com_dat):
        self.company["id"] = com_dat.company.context.sentence.position
        self.company["text"] = com_dat.company.context.get_span()
        self.company["box"] = get_box(com_dat.company)
        self.company["page"] = most_frequent(com_dat.company.context.sentence.page)
        self.company["html_attrs"] = get_html(com_dat.company)
        
        self.time["id"] = com_dat.work_time.context.sentence.position
        self.time["text"] = com_dat.work_time.context.get_span()
        self.time["box"] = get_box(com_dat.work_time)
    
    # hàm trả về True với các trường hợp đã ghép xong và các trường hợp lặp, không cần ghép nữa
    # hàm trả về False với các trường hợp chưa có đối tượng experience tương ứng
    def merge_com_pos(self,com_pos):
        if com_pos.company.context.sentence.position != self.company["id"]:
            if self.company["id_overlap"] == 0:
                box1 = self.company["box"]
                box2 = get_box(com_pos.company)
                if (get_html(com_pos.company) == self.company["html_attrs"]) and vert_distance(box1,box2) < 10 :
                    self.company["id_overlap"] = com_pos.company.context.sentence.position
                    self.company["text"] += " "
                    self.company["text"] += com_pos.company.context.get_span()
                    self.company["box"] = sum_box(box1,box2)
                    return True
        else :
            if self.position["id"] == 0:
                self.position["id"] = com_pos.position.context.sentence.position
                self.position["text"] = com_pos.position.context.get_span()
                self.position["box"] = get_box(com_pos.position)
                return True
            return True
        
        if com_pos.company.context.sentence.position == self.company["id_overlap"]:
            return True
        
        return False
    
    def merge_com_dat(self,com_dat):
        if com_dat.company.context.sentence.position != self.company["id"]:
            if self.company["id_overlap"] == 0:
                box1 = self.company["box"]
                box2 = get_box(com_dat.company)
                if (get_html(com_dat.company) == self.company["html_attrs"]) and vert_distance(box1,box2) < 10 :
                    self.company["id_overlap"] = com_dat.company.context.sentence.position
                    self.company["text"] += " "
                    self.company["text"] += com_dat.company.context.get_span()
                    self.company["box"] = sum_box(box1,box2)
                    return True
        else :
            if self.time["id"] == 0:
                self.time["id"] = com_dat.work_time.context.sentence.position
                self.time["text"] = com_dat.work_time.context.get_span()
                self.time["box"] = get_box(com_dat.work_time)
                return True
            else :
                self.time["text"] += " - "
                self.time["text"] += com_dat.work_time.context.get_span()
                box1 = self.time["box"]
                box2 = get_box(com_dat.work_time)
                self.time["box"] = sum_box(box1,box2)
                return True
        
        if com_dat.company.context.sentence.position == self.company["id_overlap"]:
            return True
        
        return False
            