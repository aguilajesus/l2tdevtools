#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to update the dependencies in various configuration files."""

from __future__ import unicode_literals

import os

from l2tdevtools import dependencies
from l2tdevtools import project_config


# TODO: generate .travis.yml


# pylint: disable=redefined-outer-name


class DependencyFileWriter(object):
  """Dependency file writer."""

  def __init__(self, project_definition, dependency_helper):
    """Initializes a dependency file writer.

    Args:
      project_definition (ProjectDefinition): project definition.
      dependency_helper (DependencyHelper): dependency helper.
    """
    super(DependencyFileWriter, self).__init__()
    self._dependency_helper = dependency_helper
    self._project_definition = project_definition


class AppveyorYmlWriter(DependencyFileWriter):
  """Appveyor.yml file writer."""

  PATH = os.path.join('appveyor.yml')

  _VERSION_PYWIN32 = '220'
  _VERSION_WMI = '1.4.9'
  _VERSION_SQLITE = '3180000'

  _DOWNLOAD_PIP = (
      '  - ps: (new-object net.webclient).DownloadFile('
      '\'https://bootstrap.pypa.io/get-pip.py\', '
      '\'C:\\Projects\\get-pip.py\')')

  _DOWNLOAD_PYWIN32 = (
      '  - ps: (new-object net.webclient).DownloadFile('
      '\'https://github.com/log2timeline/l2tbinaries/raw/master/win32/'
      'pywin32-{0:s}.win32-py2.7.exe\', '
      '\'C:\\Projects\\pywin32-{0:s}.win32-py2.7.exe\')').format(
          _VERSION_PYWIN32)

  _DOWNLOAD_WMI = (
      '  - ps: (new-object net.webclient).DownloadFile('
      '\'https://github.com/log2timeline/l2tbinaries/raw/master/win32/'
      'WMI-{0:s}.win32.exe\', \'C:\\Projects\\WMI-{0:s}.win32.exe\')').format(
          _VERSION_WMI)

  _INSTALL_PIP = (
      '  - cmd: "%PYTHON%\\\\python.exe C:\\\\Projects\\\\get-pip.py"')

  _INSTALL_PYWIN32 = (
      '  - cmd: "%PYTHON%\\\\Scripts\\\\easy_install.exe '
      'C:\\\\Projects\\\\pywin32-{0:s}.win32-py2.7.exe"').format(
          _VERSION_PYWIN32)

  _INSTALL_WMI = (
      '  - cmd: "%PYTHON%\\\\Scripts\\\\easy_install.exe '
      'C:\\\\Projects\\\\WMI-{0:s}.win32.exe"').format(_VERSION_WMI)

  _URL_L2TDEVTOOLS = 'https://github.com/log2timeline/l2tdevtools.git'

  _DOWNLOAD_L2TDEVTOOLS = (
      '  - cmd: git clone {0:s} && move l2tdevtools ..\\'.format(
          _URL_L2TDEVTOOLS))

  _FILE_HEADER = [
      'environment:',
      '  matrix:',
      '    - PYTHON: "C:\\\\Python27"',
      '',
      'install:',
      ('  - cmd: \'"C:\\Program Files\\Microsoft SDKs\\Windows\\v7.1\\Bin\\'
       'SetEnv.cmd" /x86 /release\''),
      _DOWNLOAD_PIP,
      _DOWNLOAD_PYWIN32,
      _DOWNLOAD_WMI,
      _INSTALL_PIP,
      _INSTALL_PYWIN32,
      _INSTALL_WMI,
      _DOWNLOAD_L2TDEVTOOLS]

  _DOWNLOAD_SQLITE = (
      '  - ps: (new-object net.webclient).DownloadFile('
      '\'https://www.sqlite.org/2017/sqlite-dll-win32-x86-{0:s}.zip\', '
      '\'C:\\Projects\\sqlite-dll-win32-x86-{0:s}.zip\')').format(
          _VERSION_SQLITE)

  _EXTRACT_SQLITE = (
      '  - ps: $Output = Invoke-Expression -Command '
      '"& \'C:\\\\Program Files\\\\7-Zip\\\\7z.exe\' -y '
      '-oC:\\\\Projects\\\\ x C:\\\\Projects\\\\'
      'sqlite-dll-win32-x86-{0:s}.zip 2>&1"').format(_VERSION_SQLITE)

  _INSTALL_SQLITE = (
      '  - cmd: copy C:\\Projects\\sqlite3.dll C:\\Python27\\DLLs\\')

  _SQLITE = [
      _DOWNLOAD_SQLITE,
      _EXTRACT_SQLITE,
      _INSTALL_SQLITE]

  _L2TDEVTOOLS_UPDATE = (
      '  - cmd: mkdir dependencies && set PYTHONPATH=..\\l2tdevtools && '
      '"%PYTHON%\\\\python.exe" ..\\l2tdevtools\\tools\\update.py '
      '--download-directory dependencies --machine-type x86 '
      '--msi-targetdir "%PYTHON%" --track dev {0:s}')

  _FILE_FOOTER = [
      '',
      'build: off',
      '',
      'test_script:',
      '  - "%PYTHON%\\\\python.exe run_tests.py"',
      '']

  def Write(self):
    """Writes an appveyor.yml file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = self._dependency_helper.GetL2TBinaries()
    dependencies.extend(['funcsigs', 'mock', 'pbr'])

    if 'six' not in dependencies:
      dependencies.append('six')

    if 'pysqlite' in dependencies:
      file_content.extend(self._SQLITE)

    dependencies = ' '.join(dependencies)
    l2tdevtools_update = self._L2TDEVTOOLS_UPDATE.format(dependencies)
    file_content.append(l2tdevtools_update)

    file_content.extend(self._FILE_FOOTER)

    file_content = '\n'.join(file_content)
    file_content = file_content.encode('utf-8')

    with open(self.PATH, 'wb') as file_object:
      file_object.write(file_content)


class DPKGControlWriter(DependencyFileWriter):
  """Dpkg control file writer."""

  PATH = os.path.join('config', 'dpkg', 'control')

  _PYTHON2_FILE_HEADER = [
      'Source: {project_name:s}',
      'Section: python',
      'Priority: extra',
      'Maintainer: {maintainer:s}',
      ('Build-Depends: debhelper (>= 7), python-all (>= 2.7~), '
       'python-setuptools'),
      'Standards-Version: 3.9.5',
      'X-Python-Version: >= 2.7',
      'Homepage: {homepage_url:s}',
      '']

  _PYTHON3_FILE_HEADER = [
      'Source: {project_name:s}',
      'Section: python',
      'Priority: extra',
      'Maintainer: {maintainer:s}',
      ('Build-Depends: debhelper (>= 7), python-all (>= 2.7~), '
       'python-setuptools, python3-all (>= 3.4~), python3-setuptools'),
      'Standards-Version: 3.9.5',
      'X-Python-Version: >= 2.7',
      'X-Python3-Version: >= 3.4',
      'Homepage: {homepage_url:s}',
      '']

  _DATA_PACKAGE = [
      'Package: {project_name:s}-data',
      'Architecture: all',
      'Depends: ${{misc:Depends}}',
      'Description: Data files for {name_description:s}',
      '{description_long:s}',
      '']

  _PYTHON2_PACKAGE = [
      'Package: python-{project_name:s}',
      'Architecture: all',
      ('Depends: {python2_dependencies:s}'
       '${{python:Depends}}, ${{misc:Depends}}'),
      'Description: Python 2 module of {name_description:s}',
      '{description_long:s}',
      '']

  _PYTHON3_PACKAGE = [
      'Package: python3-{project_name:s}',
      'Architecture: all',
      ('Depends: {python3_dependencies:s}'
       '${{python3:Depends}}, ${{misc:Depends}}'),
      'Description: Python 3 module of {name_description:s}',
      '{description_long:s}',
      '']

  _TOOLS_PACKAGE = [
      'Package: {project_name:s}-tools',
      'Architecture: all',
      ('Depends: python-{project_name:s}, python (>= 2.7~), '
       '${{python:Depends}}, ${{misc:Depends}}'),
      'Description: Tools of {name_description:s}',
      '{description_long:s}',
      '']

  def Write(self):
    """Writes a dpkg control file."""
    dependencies = self._dependency_helper.GetDPKGDepends()

    file_content = []

    if self._project_definition.python2_only:
      file_content.extend(self._PYTHON2_FILE_HEADER)
    else:
      file_content.extend(self._PYTHON3_FILE_HEADER)

    if os.path.isdir('data'):
      dependencies.insert(
          0, '{0:s}-data'.format(self._project_definition.name))

      file_content.extend(self._DATA_PACKAGE)

    file_content.extend(self._PYTHON2_PACKAGE)

    if not self._project_definition.python2_only:
      file_content.extend(self._PYTHON3_PACKAGE)

    if os.path.isdir('scripts') or os.path.isdir('tools'):
      file_content.extend(self._TOOLS_PACKAGE)

    description_long = self._project_definition.description_long
    description_long = '\n'.join([
        ' {0:s}'.format(line) for line in description_long.split('\n')])

    python2_dependencies = ', '.join(dependencies)
    if python2_dependencies:
      python2_dependencies = '{0:s}, '.format(python2_dependencies)

    python3_dependencies = ', '.join(dependencies).replace(
        'python', 'python3')
    if python3_dependencies:
      python3_dependencies = '{0:s}, '.format(python3_dependencies)

    kwargs = {
        'description_long': description_long,
        'description_short': self._project_definition.description_short,
        'homepage_url': self._project_definition.homepage_url,
        'maintainer': self._project_definition.maintainer,
        'name_description': self._project_definition.name_description,
        'project_name': self._project_definition.name,
        'python2_dependencies': python2_dependencies,
        'python3_dependencies': python3_dependencies}

    file_content = '\n'.join(file_content)
    file_content = file_content.format(**kwargs)

    file_content = file_content.encode('utf-8')

    with open(self.PATH, 'wb') as file_object:
      file_object.write(file_content)


class GIFTCOPRInstallScriptWriter(DependencyFileWriter):
  """GIFT COPR installation script file."""

  PATH = os.path.join('config', 'linux', 'gift_copr_install.sh')

  _FILE_HEADER = [
      '#!/usr/bin/env bash',
      'set -e',
      '',
      '# Dependencies for running Plaso, alphabetized, one per line.',
      ('# This should not include packages only required for testing or '
       'development.')]

  _ADDITIONAL_DEPENDENCIES = [
      '',
      '# Additional dependencies for running Plaso tests, alphabetized,',
      '# one per line.',
      'TEST_DEPENDENCIES="python-mock";',
      '',
      '# Additional dependencies for doing Plaso development, alphabetized,',
      '# one per line.',
      'DEVELOPMENT_DEPENDENCIES="python-sphinx',
      '                          pylint";',
      '',
      '# Additional dependencies for doing Plaso debugging, alphabetized,',
      '# one per line.']

  _FILE_FOOTER = [
      '',
      'sudo dnf install dnf-plugins-core',
      'sudo dnf copr enable @gift/dev',
      'sudo dnf install -y ${PYTHON2_DEPENDENCIES}',
      '',
      'if [[ "$*" =~ "include-debug" ]]; then',
      '    sudo dnf install -y ${DEBUG_DEPENDENCIES}',
      'fi',
      '',
      'if [[ "$*" =~ "include-development" ]]; then',
      '    sudo dnf install -y ${DEVELOPMENT_DEPENDENCIES}',
      'fi',
      '',
      'if [[ "$*" =~ "include-test" ]]; then',
      '    sudo dnf install -y ${TEST_DEPENDENCIES}',
      'fi',
      '']

  def Write(self):
    """Writes a gift_copr_install.sh file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = self._dependency_helper.GetRPMRequires(exclude_version=True)
    libyal_dependencies = []
    for index, dependency in enumerate(dependencies):
      if index == 0:
        file_content.append('PYTHON2_DEPENDENCIES="{0:s}'.format(dependency))
      elif index + 1 == len(dependencies):
        file_content.append('                      {0:s}";'.format(dependency))
      else:
        file_content.append('                      {0:s}'.format(dependency))

      if dependency.startswith('lib') and dependency.endswith('-python'):
        dependency, _, _ = dependency.partition('-')
        libyal_dependencies.append(dependency)

    file_content.extend(self._ADDITIONAL_DEPENDENCIES)

    for index, dependency in enumerate(libyal_dependencies):
      if index == 0:
        file_content.append('DEBUG_DEPENDENCIES="{0:s}-debuginfo'.format(
            dependency))
      elif index + 1 == len(libyal_dependencies):
        file_content.append('                    {0:s}-debuginfo";'.format(
            dependency))
      else:
        file_content.append('                    {0:s}-debuginfo'.format(
            dependency))

    file_content.extend(self._FILE_FOOTER)

    file_content = '\n'.join(file_content)
    file_content = file_content.encode('utf-8')

    with open(self.PATH, 'wb') as file_object:
      file_object.write(file_content)


class GIFTPPAInstallScriptWriter(DependencyFileWriter):
  """GIFT PPA installation script file."""

  PATH = os.path.join('config', 'linux', 'gift_ppa_install.sh')

  _FILE_HEADER = [
      '#!/usr/bin/env bash',
      'set -e',
      '',
      '# Dependencies for running Plaso, alphabetized, one per line.',
      ('# This should not include packages only required for testing or '
       'development.')]

  _ADDITIONAL_DEPENDENCIES = [
      '',
      '# Additional dependencies for running Plaso tests, alphabetized,',
      '# one per line.',
      'TEST_DEPENDENCIES="python-mock";',
      '',
      '# Additional dependencies for doing Plaso development, alphabetized,',
      '# one per line.',
      'DEVELOPMENT_DEPENDENCIES="python-sphinx',
      '                          pylint";',
      '',
      '# Additional dependencies for doing Plaso debugging, alphabetized,',
      '# one per line.']

  _FILE_FOOTER = [
      '',
      'sudo add-apt-repository ppa:gift/dev -y',
      'sudo apt-get update -q',
      'sudo apt-get install -y ${PYTHON2_DEPENDENCIES}',
      '',
      'if [[ "$*" =~ "include-debug" ]]; then',
      '    sudo apt-get install -y ${DEBUG_DEPENDENCIES}',
      'fi',
      '',
      'if [[ "$*" =~ "include-development" ]]; then',
      '    sudo apt-get install -y ${DEVELOPMENT_DEPENDENCIES}',
      'fi',
      '',
      'if [[ "$*" =~ "include-test" ]]; then',
      '    sudo apt-get install -y ${TEST_DEPENDENCIES}',
      'fi',
      '']

  def Write(self):
    """Writes a gift_ppa_install.sh file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = self._dependency_helper.GetDPKGDepends(exclude_version=True)
    libyal_dependencies = []
    for index, dependency in enumerate(dependencies):
      if index == 0:
        file_content.append('PYTHON2_DEPENDENCIES="{0:s}'.format(dependency))
      elif index + 1 == len(dependencies):
        file_content.append('                      {0:s}";'.format(dependency))
      else:
        file_content.append('                      {0:s}'.format(dependency))

      if dependency.startswith('lib') and dependency.endswith('-python'):
        dependency, _, _ = dependency.partition('-')
        libyal_dependencies.append(dependency)

    file_content.extend(self._ADDITIONAL_DEPENDENCIES)

    for index, dependency in enumerate(libyal_dependencies):
      if index == 0:
        file_content.append('DEBUG_DEPENDENCIES="{0:s}-dbg'.format(dependency))
      else:
        file_content.append('                    {0:s}-dbg'.format(dependency))

      file_content.append('                    {0:s}-python-dbg'.format(
          dependency))

    file_content.append('                    python-guppy";')

    file_content.extend(self._FILE_FOOTER)

    file_content = '\n'.join(file_content)
    file_content = file_content.encode('utf-8')

    with open(self.PATH, 'wb') as file_object:
      file_object.write(file_content)


class RequirementsWriter(DependencyFileWriter):
  """Requirements.txt file writer."""

  PATH = 'requirements.txt'

  _FILE_HEADER = ['pip >= 7.0.0']

  def Write(self):
    """Writes a requirements.txt file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = self._dependency_helper.GetInstallRequires()
    for dependency in dependencies:
      file_content.append('{0:s}'.format(dependency))

    file_content = '\n'.join(file_content)
    file_content = file_content.encode('utf-8')

    with open(self.PATH, 'wb') as file_object:
      file_object.write(file_content)


class SetupCfgWriter(DependencyFileWriter):
  """Setup.cfg file writer."""

  PATH = 'setup.cfg'

  _SDIST = [
      '[sdist]',
      'template = MANIFEST.in',
      'manifest = MANIFEST',
      '',
      '[sdist_test_data]',
      'template = MANIFEST.test_data.in',
      'manifest = MANIFEST.test_data',
      '']

  _BDIST_RPM = [
      '[bdist_rpm]',
      'release = 1',
      'packager = {maintainer:s}',
      'doc_files = ACKNOWLEDGEMENTS',
      '            AUTHORS',
      '            LICENSE',
      '            README',
      'build_requires = python-setuptools']

  def Write(self):
    """Writes a setup.cfg file."""
    file_content = []

    if os.path.isdir('test_data'):
      file_content.extend(self._SDIST)

    file_content.extend(self._BDIST_RPM)

    dependencies = self._dependency_helper.GetRPMRequires()
    for index, dependency in enumerate(dependencies):
      if index == 0:
        file_content.append('requires = {0:s}'.format(dependency))
      else:
        file_content.append('           {0:s}'.format(dependency))

    file_content.append('')

    kwargs = {'maintainer': self._project_definition.maintainer}

    file_content = '\n'.join(file_content)
    file_content = file_content.format(**kwargs)
    file_content = file_content.encode('utf-8')

    with open(self.PATH, 'wb') as file_object:
      file_object.write(file_content)


class TravisBeforeInstallScriptWriter(DependencyFileWriter):
  """Travis-CI install.sh file writer."""

  PATH = os.path.join('config', 'travis', 'install.sh')

  _URL_L2TDEVTOOLS = 'https://github.com/log2timeline/l2tdevtools.git'

  _FILE_HEADER = [
      '#!/bin/bash',
      '#',
      '# Script to set up Travis-CI test VM.',
      '',
      ('COVERALL_DEPENDENCIES="python-coverage python-coveralls '
       'python-docopt";'),
      '']

  _FILE_FOOTER = [
      '',
      '# Exit on error.',
      'set -e;',
      '',
      'if test ${TRAVIS_OS_NAME} = "osx";',
      'then',
      '\tgit clone {0:s};'.format(_URL_L2TDEVTOOLS),
      '',
      '\tmv l2tdevtools ../;',
      '\tmkdir dependencies;',
      '',
      ('\tPYTHONPATH=../l2tdevtools ../l2tdevtools/tools/update.py '
       '--download-directory dependencies --track dev '
       '${L2TBINARIES_DEPENDENCIES} ${L2TBINARIES_TEST_DEPENDENCIES};'),
      '',
      'elif test ${TRAVIS_OS_NAME} = "linux";',
      'then',
      '\tsudo rm -f /etc/apt/sources.list.d/travis_ci_zeromq3-source.list;',
      '',
      '\tsudo add-apt-repository ppa:gift/dev -y;',
      '\tsudo apt-get update -q;',
      '\t# Only install the Python 2 dependencies.',
      ('\t# Also see: https://docs.travis-ci.com/user/languages/python/'
       '#Travis-CI-Uses-Isolated-virtualenvs'),
      ('\tsudo apt-get install -y ${COVERALL_DEPENDENCIES} '
       '${PYTHON2_DEPENDENCIES} ${PYTHON2_TEST_DEPENDENCIES};'),
      'fi',
      '']

  def Write(self):
    """Writes an install.sh file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = self._dependency_helper.GetL2TBinaries()
    dependencies = ' '.join(dependencies)
    file_content.append('L2TBINARIES_DEPENDENCIES="{0:s}";'.format(
        dependencies))

    file_content.append('')

    if 'six' in dependencies:
      file_content.append(
          'L2TBINARIES_TEST_DEPENDENCIES="funcsigs mock pbr";')
    else:
      file_content.append(
          'L2TBINARIES_TEST_DEPENDENCIES="funcsigs mock pbr six";')

    file_content.append('')

    dependencies = self._dependency_helper.GetDPKGDepends(exclude_version=True)
    dependencies = ' '.join(dependencies)
    file_content.append('PYTHON2_DEPENDENCIES="{0:s}";'.format(dependencies))

    file_content.append('')
    file_content.append('PYTHON2_TEST_DEPENDENCIES="python-mock python-tox";')

    file_content.extend(self._FILE_FOOTER)

    file_content = '\n'.join(file_content)
    file_content = file_content.encode('utf-8')

    with open(self.PATH, 'wb') as file_object:
      file_object.write(file_content)


class ToxIniWriter(DependencyFileWriter):
  """Tox.ini file writer."""

  PATH = 'tox.ini'

  _FILE_CONTENT = '\n'.join([
      '[tox]',
      'envlist = py2, py3',
      '',
      '[testenv]',
      'pip_pre = True',
      'setenv =',
      '    PYTHONPATH = {{toxinidir}}',
      'deps =',
      '    coverage',
      '    mock',
      '    pytest',
      '    -rrequirements.txt',
      'commands =',
      '    ./run_tests.py',
      '',
      '[testenv:py27]',
      'pip_pre = True',
      'setenv =',
      '    PYTHONPATH = {{toxinidir}}',
      'deps =',
      '    coverage',
      '    mock',
      '    pytest',
      '    -rrequirements.txt',
      'commands =',
      '    coverage erase',
      ('    coverage run --source={project_name:s} '
       '--omit="*_test*,*__init__*,*test_lib*" run_tests.py'),
      ''])

  def Write(self):
    """Writes a setup.cfg file."""
    kwargs = {'project_name': self._project_definition.name}
    file_content = self._FILE_CONTENT.format(**kwargs)

    file_content = file_content.encode('utf-8')

    with open(self.PATH, 'wb') as file_object:
      file_object.write(file_content)


if __name__ == '__main__':
  project_file = os.getcwd()
  project_file = os.path.basename(project_file)
  project_file = '{0:s}.ini'.format(project_file)

  project_reader = project_config.ProjectDefinitionReader()
  with open(project_file, 'rb') as file_object:
    project_definition = project_reader.Read(file_object)

  helper = dependencies.DependencyHelper()

  for writer_class in (
      AppveyorYmlWriter, RequirementsWriter, SetupCfgWriter,
      TravisBeforeInstallScriptWriter, ToxIniWriter):
    writer = writer_class(project_definition, helper)
    writer.Write()

  for writer_class in (
      DPKGControlWriter, GIFTCOPRInstallScriptWriter,
      GIFTPPAInstallScriptWriter):
    if not os.path.exists(writer_class.PATH):
      continue

    writer = writer_class(project_definition, helper)
    writer.Write()

  l2tdevtools_path = os.path.abspath(__file__)
  l2tdevtools_path = os.path.dirname(l2tdevtools_path)
  l2tdevtools_path = os.path.dirname(l2tdevtools_path)

  path = os.path.join(l2tdevtools_path, 'l2tdevtools', 'dependencies.py')
  file_data = []
  with open(path, 'rb') as file_object:
    for line in file_object.readlines():
      if 'GetDPKGDepends' in line:
        break

      file_data.append(line)

  file_data.pop()
  file_data = ''.join(file_data)

  path = os.path.join('utils', 'dependencies.py')
  with open(path, 'wb') as file_object:
    file_object.write(file_data)
