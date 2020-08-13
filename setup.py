import cx_Freeze

executables = [cx_Freeze.Executable("Anti-Plague.py", base="Win32GUI")]
cx_Freeze.setup(name="Anti Plague Simulator",
                options={"build_exe": {'packages': ['pygame'], 'include_files': ['Data/']}},
                executables=executables
                )
