#!C:\Python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'mpyq==0.2.5','console_scripts','mpyq'
__requires__ = 'mpyq==0.2.5'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('mpyq==0.2.5', 'console_scripts', 'mpyq')()
    )
