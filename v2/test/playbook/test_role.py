# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import patch, MagicMock

from ansible.errors import AnsibleParserError
from ansible.playbook.block import Block
from ansible.playbook.role import Role
from ansible.playbook.task import Task

from ansible.parsing.yaml import DataLoader

class TestRole(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_construct_empty_block(self):
        r = Role()

    @patch.object(DataLoader, 'load_from_file')
    def test__load_role_yaml(self, _load_from_file):
        _load_from_file.return_value = dict(foo='bar')
        r = Role()
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=True):
                res = r._load_role_yaml('/fake/path', 'some_subdir')
                self.assertEqual(res, dict(foo='bar'))

    def test_role__load_list_of_blocks(self):
        task = dict(action='test')
        r = Role()
        self.assertEqual(r._load_list_of_blocks([]), [])
        res = r._load_list_of_blocks([task])
        self.assertEqual(len(res), 1)
        assert isinstance(res[0], Block)
        res = r._load_list_of_blocks([task,task,task])
        self.assertEqual(len(res), 3)

    @patch.object(Role, '_get_role_path')
    @patch.object(Role, '_load_role_yaml')
    def test_load_role_with_tasks(self, _load_role_yaml, _get_role_path):

        _get_role_path.return_value = ('foo', '/etc/ansible/roles/foo')

        def fake_load_role_yaml(role_path, subdir):
            if role_path == '/etc/ansible/roles/foo':
                if subdir == 'tasks':
                    return [dict(shell='echo "hello world"')]
            return None

        _load_role_yaml.side_effect = fake_load_role_yaml

        r = Role.load('foo')
        self.assertEqual(len(r.task_blocks), 1)
        assert isinstance(r.task_blocks[0], Block)

    @patch.object(Role, '_get_role_path')
    @patch.object(Role, '_load_role_yaml')
    def test_load_role_with_handlers(self, _load_role_yaml, _get_role_path):

        _get_role_path.return_value = ('foo', '/etc/ansible/roles/foo')

        def fake_load_role_yaml(role_path, subdir):
            if role_path == '/etc/ansible/roles/foo':
                if subdir == 'handlers':
                    return [dict(name='test handler', shell='echo "hello world"')]
            return None

        _load_role_yaml.side_effect = fake_load_role_yaml

        r = Role.load('foo')
        self.assertEqual(len(r.handler_blocks), 1)
        assert isinstance(r.handler_blocks[0], Block)

    @patch.object(Role, '_get_role_path')
    @patch.object(Role, '_load_role_yaml')
    def test_load_role_with_vars(self, _load_role_yaml, _get_role_path):

        _get_role_path.return_value = ('foo', '/etc/ansible/roles/foo')

        def fake_load_role_yaml(role_path, subdir):
            if role_path == '/etc/ansible/roles/foo':
                if subdir == 'defaults':
                    return dict(foo='bar')
                elif subdir == 'vars':
                    return dict(foo='bam')
            return None

        _load_role_yaml.side_effect = fake_load_role_yaml

        r = Role.load('foo')
        self.assertEqual(r.default_vars, dict(foo='bar'))
        self.assertEqual(r.role_vars, dict(foo='bam'))

    @patch.object(Role, '_get_role_path')
    @patch.object(Role, '_load_role_yaml')
    def test_load_role_with_metadata(self, _load_role_yaml, _get_role_path):

        def fake_load_role_yaml(role_path, subdir):
            if role_path == '/etc/ansible/roles/foo':
                if subdir == 'meta':
                    return dict(dependencies=['bar'], allow_duplicates=True, galaxy_info=dict(a='1', b='2', c='3'))
            elif role_path == '/etc/ansible/roles/bad1':
                if subdir == 'meta':
                    return 1
            elif role_path == '/etc/ansible/roles/bad2':
                if subdir == 'meta':
                    return dict(foo='bar')
            return None

        _load_role_yaml.side_effect = fake_load_role_yaml

        _get_role_path.return_value = ('foo', '/etc/ansible/roles/foo')

        r = Role.load('foo')
        self.assertEqual(r.dependencies, ['bar'])
        self.assertEqual(r.allow_duplicates, True)
        self.assertEqual(r.galaxy_info, dict(a='1', b='2', c='3'))

        _get_role_path.return_value = ('bad1', '/etc/ansible/roles/bad1')
        self.assertRaises(AnsibleParserError, Role.load, 'bad1')

        _get_role_path.return_value = ('bad2', '/etc/ansible/roles/bad2')
        self.assertRaises(AnsibleParserError, Role.load, 'bad2')

    @patch.object(Role, '_get_role_path')
    @patch.object(Role, '_load_role_yaml')
    def test_load_role_complex(self, _load_role_yaml, _get_role_path):

        _get_role_path.return_value = ('foo', '/etc/ansible/roles/foo')

        def fake_load_role_yaml(role_path, subdir):
            if role_path == '/etc/ansible/roles/foo':
                if subdir == 'tasks':
                    return [dict(shell='echo "hello world"')]
            return None

        _load_role_yaml.side_effect = fake_load_role_yaml

        r = Role.load(dict(role='foo'))


