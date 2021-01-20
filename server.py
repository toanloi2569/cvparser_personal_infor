import sys
import os

# from cv_parser.main import CvParser
from vi_cv_parser.main import CvParser as ViCvParser
from flask import Flask, jsonify, request, flash 
import json
import subprocess
import os 
import shutil
import random
import logging

try:
    from flask_cors import CORS  # The typical way to import flask-cors
except ImportError:
    # Path hack allows examples to be run without installation.
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)

    from flask_cors import CORS

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)
logging.basicConfig(level=logging.INFO)

TMP_PATH = 'temporary_data/'

DATA_PATH = 'data/'

vi_cv_parser = ViCvParser()

@app.route('/parser', methods=['POST'])
def get_request():
	pdf_file = request.files.getlist('file')[0]
	check_folder()

	rand = random.randint(0,1000000)
	path_file = TMP_PATH + str(rand) + '/'
	while os.path.isdir(path_file):
		rand = random.randint(0,1000000)
		path_file = TMP_PATH + str(rand) + '/'
	os.mkdir(path_file)
	pdf_file.save('%s/%s' %(path_file, pdf_file.filename.replace(" ","_")))

	# cv_parser = CvParser()

	result = None
	# try:
	if language(path_file) == 'vi':
		document = vi_cv_parser.parse(path_file)
		result = vi_cv_parser.extract_data(document)
		result = vi_cv_parser.get_list_json(result)
	else:
		# TODO parser for english cv
		result = cv_parser.get_list_json()

	clear(path_file)
	return jsonify(result), 200

	# except:
	# 	return jsonify({"error": "can't parse file"}), 400

def check_folder():
	if not os.path.isdir(TMP_PATH):
		os.mkdir(TMP_PATH)
	if not os.path.isdir(DATA_PATH):
		os.mkdir(DATA_PATH)

def clear(path_file):
	for filename in os.listdir(path_file):
		if filename.endswith('.pdf'):
			shutil.copyfile(path_file + filename, 
				'%s%s' %(DATA_PATH, filename))
			logging.info(f'\tFile {filename} is saved at {DATA_PATH}{filename}')
			logging.info(f'\tParsed file')

	shutil.rmtree(path_file)

def language(path_file):
	return 'vi'

			
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port listening')
    args = parser.parse_args()
    port = args.port
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True, processes=1)
