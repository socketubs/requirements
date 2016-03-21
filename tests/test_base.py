import os
import sys
import shutil
import tempfile
from unittest import TestCase

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from requirements import Requirement
from requirements import Requirements

ORIGINAL_DIRECTORY = os.getcwd()


class RequirementsTestCase(TestCase):
    def setUp(self):
        self.root_directory = tempfile.mkdtemp()
        os.chdir(self.root_directory)

        self.r = Requirements()

    def tearDown(self):
        os.chdir(ORIGINAL_DIRECTORY)
        shutil.rmtree(self.root_directory)

    def test_requirement_repr(self):
        r = Requirement.parse('requests==2.9.1')
        self.assertEqual(r.__repr__(), '<Requirement: "requests==2.9.1">')

    def test_requirement_parsing(self):
        line = '  requests==2.9.1,>=2.8.1 # jambon'
        r = Requirement.parse(line)
        self.assertEqual(r.line, line)
        self.assertEqual(r.name, 'requests')
        self.assertEqual(r.specs, [('==', '2.9.1'), ('>=', '2.8.1')])

    def test_detect_files(self):
        requirements_path = os.path.join(
            self.root_directory, 'requirements.txt')

        with open(requirements_path, 'w') as f:
            f.write('requests==2.9.1\n')

        os.mkdir(os.path.join(self.root_directory, 'requirements'))
        tests_requirements_path = os.path.join(
            self.root_directory, 'requirements', 'tests.txt')

        with open(tests_requirements_path, 'w') as f:
            f.write('flake8==2.5.4\n')

        dependencies = self.r.dependencies
        self.assertEqual(dependencies['tests_require'], ['flake8 == 2.5.4'])
        self.assertEqual(
            dependencies['install_requires'], ['requests == 2.9.1'])
        self.assertEqual(dependencies['dependency_links'], [])

    def test_different_paths(self):
        requirements_path = os.path.join(
            self.root_directory, 'foo.txt')

        with open(requirements_path, 'w') as f:
            f.write('requests==2.9.1\n')

        os.mkdir(os.path.join(self.root_directory, 'moar-requirements'))
        tests_requirements_path = os.path.join(
            self.root_directory, 'moar-requirements', 'bar.txt')

        with open(tests_requirements_path, 'w') as f:
            f.write('flake8==2.5.4\n')

        self.r.requirements_path = requirements_path
        self.r.tests_requirements_path = tests_requirements_path

        dependencies = self.r.dependencies
        self.assertEqual(dependencies['tests_require'], ['flake8 == 2.5.4'])
        self.assertEqual(
            dependencies['install_requires'], ['requests == 2.9.1'])
        self.assertEqual(dependencies['dependency_links'], [])

    def test_empty_lines(self):
        requirements_path = os.path.join(
            self.root_directory, 'requirements.txt')

        with open(requirements_path, 'w') as f:
            f.write('\n\n')
            f.write('requests==2.9.1 #I like ham\n')
            f.write('\n')
            f.write('boto')

        dependencies = self.r.dependencies
        self.assertEqual(
            sorted(dependencies['install_requires']),
            sorted(['requests == 2.9.1', 'boto']))

    def test_comments_line_ignored(self):
        requirements_path = os.path.join(
            self.root_directory, 'requirements.txt')

        with open(requirements_path, 'w') as f:
            f.write('# boto==python3-lol\n')
            f.write('requests==2.9.1 #I like ham\n')

        os.mkdir(os.path.join(self.root_directory, 'requirements'))
        tests_requirements_path = os.path.join(
            self.root_directory, 'requirements', 'tests.txt')

        with open(tests_requirements_path, 'w') as f:
            f.write('flake8==2.5.4\n')

        dependencies = self.r.dependencies
        self.assertEqual(dependencies['tests_require'], ['flake8 == 2.5.4'])
        self.assertEqual(dependencies['install_requires'], ['requests == 2.9.1'])
        self.assertEqual(dependencies['dependency_links'], [])

    def test_multi_specifiers(self):
        requirements_path = os.path.join(
            self.root_directory, 'requirements.txt')
        tests_requirements_path = os.path.join(
            self.root_directory, 'tests-requirements.txt')

        with open(requirements_path, 'w') as f:
            f.write('requests<=2.9.1,>=2.8.5')

        with open(tests_requirements_path, 'w') as f:
            f.write('requests   <=  2.9.1 , >=2.8.5')

        self.r.tests_requirements_path = 'tests-requirements.txt'

        dependencies = self.r.dependencies
        self.assertEqual(
            dependencies['install_requires'], ['requests <= 2.9.1, >= 2.8.5'])
        self.assertEqual(
            dependencies['tests_require'], ['requests <= 2.9.1, >= 2.8.5'])

    def test_ignore_every_private_links(self):
        requirements_path = os.path.join(
            self.root_directory, 'requirements.txt')

        with open(requirements_path, 'w') as f:
            f.write('--no-index --find-links=/tmp/wheelhouse SomePackage\n')
            f.write('--find-links=/tmp/wheelhouse SomePackage\n')
            f.write('-f /tmp/wheelhouse SomePackage\n')
            f.write('--extra-index-url http://foo.bar SomePackage\n')
            f.write('-i http://foo.bar SomePackage\n')
            f.write('requests\n')
            f.write('--index-url http://foo.bar SomePackage\n')

        dependencies = self.r.dependencies
        self.assertEqual(dependencies['install_requires'], ['requests'])

    def test_ignore_arguments(self):
        requirements_path = os.path.join(
            self.root_directory, 'requirements.txt')

        with open(requirements_path, 'w') as f:
            f.write('requests\n')
            f.write('--always-unzip SomePackage\n')
            f.write('-Z SomePackage\n')

        dependencies = self.r.dependencies
        self.assertEqual(dependencies['install_requires'], ['requests'])

    def test_requirements_inception(self):
        requirements_path = os.path.join(
            self.root_directory, 'requirements.txt')
        requirements_path_02 = os.path.join(
            self.root_directory, 'requirements-02.txt')
        requirements_path_03 = os.path.join(
            self.root_directory, 'requirements', 'requirements-03.txt')

        os.mkdir(os.path.join(self.root_directory, 'requirements'))

        with open(requirements_path, 'w') as f:
            f.write('requests\n')
            f.write('-r requirements-02.txt\n')

        with open(requirements_path_02, 'w') as f:
            f.write('boto\n')
            f.write('--requirement requirements/requirements-03.txt\n')

        with open(requirements_path_03, 'w') as f:
            f.write('isit==0.1.0\n')

        dependencies = self.r.dependencies
        self.assertEqual(
            sorted(dependencies['install_requires']),
            sorted(['requests', 'boto', 'isit == 0.1.0']))

    def test_dependency_links(self):
        requirements_path = os.path.join(
            self.root_directory, 'requirements.txt')

        with open(requirements_path, 'w') as f:
            f.write('boto\n')
            f.write('-e git+https://github.com/kennethreitz/requests.git@master#egg=requests\n')
            f.write('-e svn+http://foo:bar@svn.myproject.org/svn/MyProject/trunk@2019#egg=foo01    # COMMENT\n')
            f.write('-e git+ssh://git@myproject.org/MyProject/#egg=foo02\n')
            f.write('-e hg+http://hg.myproject.org/MyProject/@da39a3ee5e6b#egg=foo03\n')
            f.write('-e bzr+https://bzr.myproject.org/MyProject/trunk/@2019#egg=foo04\n')

        dependencies = self.r.dependencies
        self.assertEqual(
            sorted(dependencies['install_requires']),
            sorted(['requests', 'boto', 'foo01', 'foo02', 'foo03', 'foo04']))
        self.assertEqual(
            sorted(dependencies['dependency_links']),
            sorted([
                'git+https://github.com/kennethreitz/requests.git@master#egg=requests',
                'svn+http://foo:bar@svn.myproject.org/svn/MyProject/trunk@2019#egg=foo01',
                'git+ssh://git@myproject.org/MyProject/#egg=foo02',
                'hg+http://hg.myproject.org/MyProject/@da39a3ee5e6b#egg=foo03',
                'bzr+https://bzr.myproject.org/MyProject/trunk/@2019#egg=foo04']))

    def test_http_link(self):
        requirements_path = os.path.join(
            self.root_directory, 'requirements.txt')

        with open(requirements_path, 'w') as f:
            f.write('boto\n')
            f.write('http://someserver.org/packages/MyPackage-3.0.tar.gz#egg=foo\n')

        dependencies = self.r.dependencies
        self.assertEqual(
            sorted(dependencies['install_requires']), sorted(['boto', 'foo']))
        self.assertEqual(
            sorted(dependencies['dependency_links']),
            sorted([
                'http://someserver.org/packages/MyPackage-3.0.tar.gz#egg=foo']))
