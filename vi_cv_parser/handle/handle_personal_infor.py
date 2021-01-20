from vi_cv_parser.handle.utils import *

def personal_infor_to_json(result,Name,Email,Birthday,Address,Phone):
    
    for c in Name:
        sent = c.name.context.sentence
        result[sent.document.name]["infor"]["name"]["text"].add(c.name.context.get_span())
        
        result[sent.document.name]["infor"]["name"]["box"] = get_box(c.name)
        
    for c in Email:
        sent = c.email.context.sentence    
        if len(result[sent.document.name]["infor"]["email"]["text"]) == 0:
            result[sent.document.name]["infor"]["email"]["text"].add(c.email.context.get_span())
            result[sent.document.name]["infor"]["email"]["box"] = get_box(c.email)
        else:
            box1 = result[sent.document.name]["infor"]["email"]["box"]
            box2 = get_box(c.email)
            if box2[1] < box1[1]:
                result[sent.document.name]["infor"]["email"]["text"].pop()
                result[sent.document.name]["infor"]["email"]["text"].add(c.email.context.get_span())
                result[sent.document.name]["infor"]["email"]["box"] = get_box(c.email)
        
    for c in Birthday:
        sent = c.birthday.context.sentence
        if len(result[sent.document.name]["infor"]["birthday"]["text"]) == 0:
            result[sent.document.name]["infor"]["birthday"]["text"].add(c.birthday.context.get_span())
            result[sent.document.name]["infor"]["birthday"]["box"] = get_box(c.birthday)
        
    for c in Phone:
        sent = c.phone.context.sentence
        result[sent.document.name]["infor"]["phone"]["text"].add(c.phone.context.get_span())
        
        result[sent.document.name]["infor"]["phone"]["box"] = get_box(c.phone)
        
    for c in Address:
        sent = c.address.context.sentence
        box = result[sent.document.name]["infor"]["address"]["box"]
        box2 = get_box(c.address)
        if result[sent.document.name]["infor"]["address"]["text"] == "" or (vert_distance(box,box2) < 15 and align_vertical(box,box2)):
            result[sent.document.name]["infor"]["address"]["text"] += c.address.context.get_span()

            top = max(sent.top,key=sent.top.count)
            bottom = max(sent.bottom,key=sent.bottom.count)
            left = c.address.context.get_attrib_tokens("left")[0]
            right = c.address.context.get_attrib_tokens("right")[-1]

            box[0] =  left if left < box[0] else box[0]
            box[1] =  top if top < box[1] else box[1]
            box[2] =  right if right > box[2] else box[2]
            box[3] =  bottom if bottom > box[3] else box[3]
    for d in result:
        result[d]["infor"]["name"]["text"] = result[d]["infor"]["name"]["text"].pop() if len(result[d]["infor"]["name"]["text"]) != 0 else ""
        result[d]["infor"]["email"]["text"] = result[d]["infor"]["email"]["text"].pop() if len(result[d]["infor"]["email"]["text"]) != 0 else ""
        result[d]["infor"]["birthday"]["text"] = result[d]["infor"]["birthday"]["text"].pop() if len(result[d]["infor"]["birthday"]["text"]) != 0 else ""
        result[d]["infor"]["phone"]["text"] = result[d]["infor"]["phone"]["text"].pop() if len(result[d]["infor"]["phone"]["text"]) != 0 else ""
    return result