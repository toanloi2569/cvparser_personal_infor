from fonduer.candidates.models.implicit_span_mention import TemporarySpanMention
from fonduer.candidates.mentions import MentionNgrams , MentionSentences
from fonduer.candidates.matchers import RegexMatchSpan,RegexMatchEach, LambdaFunctionMatcher, Intersect, Union
from fonduer.utils.data_model_utils import *
from fonduer.candidates.models import Mention, mention_subclass
from fonduer.candidates import MentionExtractor
from fonduer.candidates.mentions import MentionExtractorUDF
from fonduer.parser.models import Document

import re
flags = re.IGNORECASE|re.MULTILINE|re.UNICODE


def regex_emails():
    emails = {}

    emails['rgx1'] = u"^[a-z][a-z0-9_\.]{5,32}@[a-z0-9]{2,}(\.[a-z0-9]{2,4}){1,2}$"
    emails['rgx2'] = u"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9.-]+\.[A-Z]{2,}$"
    emails['rgx3'] = u"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    emails['rgx4'] = u"(\W|^)[\w.+\-]*@[a-z0-9]{2,}((\.[a-z0-9]{2,4}){1,2}$)?"
    
    emails['email'] = email =  emails['rgx1'] + "|" + emails['rgx2'] + "|" + emails['rgx3'] + "|" + emails['rgx4'] 
 
    return emails
    

class MentionEmails(MentionSentences):
    """Defines the space of Mentions as date patterns in a Document *x*."""
    flags = re.IGNORECASE|re.MULTILINE|re.UNICODE
    emails = regex_emails()

    def __init__(self):
        """Initialize MentionSentences."""
        MentionSentences.__init__(self)
        
    # convert list to string
    def convert(list):      
        s = [str(i) for i in list]    
        # Join list items using join() 
        res = "".join(s)
        return(res) 
    
    def graftEmail(text):
        list_text = list(text)
        index = text.index("@")
        if index > 0 and index < len(list_text)-1 and (list_text[index-1] == " " or list_text[index+1] == " "):
            list_text.pop(index-1)
            list_text.pop(index)
        return MentionEmails.convert(list_text)
        
    def extract_emails(self, text):
        for match in re.finditer(re.compile(MentionEmails.emails['email'], flags), MentionEmails.graftEmail(text)):
            s = match.start()
            e = match.end() + 3
            yield (s, e, text[s:e])    

    def apply(self, doc):
        """
        Generate MentionSentences from a Document by parsing all of its Sentences.
        :param doc: The ``Document`` to parse.
        :type doc: ``Document``
        :raises TypeError: If the input doc is not of type ``Document``.
        """
        if not isinstance(doc, Document):
            raise TypeError(
                "Input Contexts to MentionSentences.apply() must be of type Document"
            )

        for sentence in doc.sentences:
            if sentence.text.find("@") != -1:
                for email_mention in self.extract_emails(sentence.text):
                    yield TemporarySpanMention(
                        char_start=email_mention[0], 
                        char_end=email_mention[1] - 1, 
                        sentence=sentence
                    )
def email_mc(mention):
    return 1

def email_extract(docs, session, email_subclass, parallelism, clear=True):
    email_matcher = LambdaFunctionMatcher(func=email_mc, longest_match_only= True)
    email_space = MentionEmails()
    mention_extractor = MentionExtractor(session, [email_subclass], [email_space], [email_matcher])
    mention_extractor.apply(docs, parallelism=parallelism, clear=clear)

def email_extract_server(document, email_subclass):
    email_matcher = LambdaFunctionMatcher(func=email_mc, longest_match_only= True)
    email_space = MentionEmails()

    document = MentionExtractorUDF([email_subclass], [email_space], [email_matcher]).apply(document)
    return document
