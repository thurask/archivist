from cx_Freeze import setup, Executable
from os.path import join, abspath, dirname

# Dependencies are automatically detected, but it might need
# fine tuning.
localdir = dirname(abspath(__file__))
buildOptions = dict(packages=[],
                    includes=[
    join(localdir, "filehashtools.py"),
    join(localdir, "pseudocap.py"),
    join(localdir, "filters.py")
],
    excludes=[],
    include_msvcr=[True],
    build_exe="archivist",
    zip_includes=[])

base = 'Console'

executables = [
    Executable('archivist.py',
               base=base,
               appendScriptToExe=True,
               appendScriptToLibrary=False)
]

setup(name='archivist',
      version='1.0.0.0',
      description='Downloads bar files, creates autoloaders',
      options=dict(
          build_exe=buildOptions),
      executables=executables)


# # TO BUILD:
# # >python setup.py build_exe
