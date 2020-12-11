SET _path=%cd%
for %%a in ("%_path%") do set "ROOT_DIR=%%~dpa"

python -m venv %ROOT_DIR%env

%ROOT_DIR%env\Scripts\pip install -r %ROOT_DIR%requirements.txt

%ROOT_DIR%env\Scripts\python %ROOT_DIR%manage.py makemigrations
%ROOT_DIR%env\Scripts\python %ROOT_DIR%manage.py migrate
%ROOT_DIR%env\Scripts\python %ROOT_DIR%manage.py loaddata %ROOT_DIR%initial_interval_data.json