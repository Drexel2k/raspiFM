import os
import sys
import ctypes

serialization_directory = os.path.expanduser('~/raspifm')
web_defaultlanguage="german"
web_defaultcountry="DE"
touch_startfullscreen = False

# Windows directory support is only for developing on windows machines
if(sys.platform == "win32"):
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 0   # Get current, not default value

    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    serialization_directory = buf.value + "\\raspifm"
else:
    if not(sys.platform == "linux"): 
        raise OSError("OS not supported, only linux and windows")