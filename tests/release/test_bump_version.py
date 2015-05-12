import os
import unittest

from maintain.commands.release import bump_version_file
from ..utils import temp_directory, touch


class BumpVersionTestCase(unittest.TestCase):
    def test_doesnt_write_version_file_when_non_existant(self):
        with temp_directory() as directory:
            bump_version_file('2.3.0')
            self.assertFalse(os.path.exists('VERSION'))

    def test_bumps_version_file(self):
        with temp_directory() as directory:
            touch('VERSION', '2.2.12')
            bump_version_file('2.3.0')

            with open('VERSION') as fp:
                self.assertEqual(fp.read(), '2.3.0')
