CALL scripts\activate
CALL python -m PyInstaller -y -F -w -i "images\wizard.ico" "source\core.py"
