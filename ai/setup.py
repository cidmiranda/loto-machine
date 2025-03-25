import sys

if sys.platform == "win32":
    platform_supported = True
    lib_talib_name = 'ta_libc_cdr'
    include_dirs = [r"c:\ta-lib\include"]
    lib_talib_dirs = [r"c:\ta-lib\lib"]