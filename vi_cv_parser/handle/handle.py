def build_json(docs):
    result = dict()
    for doc in docs:
        result[doc.name] = {
            "infor" : {
                "name" : {
                    "text" : set(),
                    "box" : [700,900,0,0] # [left,top,right,bottom], trục x từ trái sang, trục y từ trên xuống
                },
                "email" : {
                    "text" : set(),
                    "box" : [700,900,0,0]
                },
                "phone" : {
                    "text" : set(),
                    "box" : [700,900,0,0]
                },
                "birthday" : {
                    "text" : set(),
                    "box" : [700,900,0,0]
                },
                "address" : {
                    "text" : "",
                    "box" : [700,900,0,0]
                },
            },
            "experience" : [],
            "education" : [],
            "skill" : []
        }
        
    return result