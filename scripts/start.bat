SET _path=%cd%
for %%a in ("%_path%") do set "ROOT_DIR=%%~dpa"

IF not exist %ROOT_DIR%env (
    CALL install.bat
)

cd ../ & %ROOT_DIR%env\Scripts\python %ROOT_DIR%manage.py runserver
