from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], includes = [], excludes = [], include_msvcr =[True])

base = 'Console'

executables = [
    Executable('archivist.py', base=base)
]

setup(name='archivist',
      version = '2014-04-12-A',
      description = 'Downloads bar files, creates autoloaders',
      options = dict(build_exe = buildOptions),
      executables = executables)

#TO BUILD:
#>python setup.py build_exe
