import codecs
import os
from typing import Iterator
import subprocess
import sys

from lxml import etree
from bs4 import BeautifulSoup
from fonduer.utils.layout_parser import analysis
from fonduer.parser.models import Document
from fonduer.parser.preprocessors.doc_preprocessor import DocPreprocessor


class XMLDocPreprocessor(DocPreprocessor):
    """A generator which processes an XML file or directory of XML files into
    a set of Document objects.

    :param encoding: file encoding to use (e.g. "utf-8").
    :type encoding: str
    :param path: filesystem path to file or directory to parse.
    :type path: str
    :param max_docs: the maximum number of ``Documents`` to produce.
    :type max_docs: int
    :rtype: A generator of ``Documents``.
    """

    def _parse_file(self, fp: str, file_name: str) -> Iterator[Document]:
        xml_content = subprocess.check_output(
            f"pdf2txt.py -t xml -M 3 -m 5 -A '{fp}' ", shell=True
        )
        soup = BeautifulSoup(xml_content, "lxml")
        all_xml_elements = soup.find_all("pages")
        if len(all_xml_elements) != 1:
            raise NotImplementedError(
                f"unsupported format file: {file_name}"
            )
        text = all_xml_elements[0]
        tree = etree.fromstring(str(text))
        try:
            tree = analysis(tree)
        except Exception as e:
            print(e)
            pass

        name = os.path.basename(fp)[: os.path.basename(fp).rfind(".")]
        stable_id = self._get_stable_id(name)
        print(name)
        yield Document(
            name=name,
            stable_id=stable_id,
            text=etree.tostring(tree),
            meta={"file_name": file_name},
        )

    def __len__(self) -> int:
        """Provide a len attribute based on max_docs and number of files in folder."""
        num_docs = min(len(self.all_files), self.max_docs)
        return num_docs

    def _can_read(self, fpath: str) -> bool:
        return fpath.lower().endswith("pdf") 
