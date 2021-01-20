from vi_cv_parser.utils import parse_font, parse_size

def sum_box(box1,box2):
    left = min(box1[0],box2[0])
    top = min(box1[1],box2[1])
    right = max(box1[2],box2[2])
    bottom = max(box1[3],box2[3])
    return [left,top,right,bottom]
     
## hàm lấy toạ đồ hình chữ nhật bao của mention
def get_box(mention):
    top=min(mention.context.get_attrib_tokens("top"))
    bottom=max(mention.context.get_attrib_tokens("bottom"))
    left = mention.context.get_attrib_tokens("left")[0]
    right = max(mention.context.get_attrib_tokens("right"))
    return [left,top,right,bottom]

def align_vertical(box1,box2):
    if abs(box1[0] - box2[0]) < 5:
        return True
    elif abs(box1[2] - box2[2]) < 5:
        return True
    else:
        return False
def most_frequent(pos):
    return max(pos, key=pos.count)
    
## hàm so khoảng cách theo chiều dọc (khoảng cách giữa hai dòng)
def vert_distance(box1,box2):
    top1= box1[1]
    bottom1= box1[3]
    
    top2= box2[1]
    bottom2= box2[3]
    return min(abs(bottom1-top2),abs(bottom2-top1),abs(top1-top2))        

def horizontal_distance(box1, box2):
    left1= box1[0]
    right1 = box1[2]

    left2= box2[0]
    right2 = box2[2]
    return min(abs(left1-right2), abs(left2-right1))

def get_html(mention):
    font = parse_font(mention.context.sentence.html_attrs[0])
    size = parse_size(mention.context.sentence.html_attrs[0])
    return (str(font)+str(size))