from vi_cv_parser.handle.utils import *

def skill_to_json(result, Skill):
    for c in Skill:
        result[c.skill.context.sentence.document.name]["skill"].append({
            "text": c.skill.context.get_span(),
            "box" : get_box(c.skill),
            "page" : c.skill.context.sentence.page[0]
        })
    return result
        