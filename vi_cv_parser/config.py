# -------------------------------------------------------------------------------
# Postgresql đa luồng
MODEL_PATH = 'vi_cv_parser/model'

PARALLEL = 8
ATTRIBUTE = "personal_information"
USER = 'postgres'
PASSWORD = '20162569'
conn_string = 'postgresql://%s:%s@localhost:5432/%s' %(USER, PASSWORD, ATTRIBUTE)

SKILL_EXTRACTOR = 'http://localhost:5001/'
NER = 'http://localhost:5002/'

# -------------------------------------------------------------------------------
# Postgresql đơn luồng
# PARALLEL = 1
# ATTRIBUTE = "personal_information"
# USER = 'postgres'
# PASSWORD = '20162569'
# conn_string = 'postgresql://%s:%s@localhost:5432/%s' %(USER, PASSWORD, ATTRIBUTE)

# -------------------------------------------------------------------------------
# Sqlite đa luồng
# PARALLEL = 4
# conn_string = 'sqlite://'

# -------------------------------------------------------------------------------
# Sqlite đơn luồng
# PARALLEL = 1
# conn_string = 'sqlite://'


