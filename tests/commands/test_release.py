import unittest

from click.testing import CliRunner

from maintain.commands.release import release


class ReleaseCommandTestCase(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_requires_version_with_bump(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(release, [])

            self.assertTrue('Error: Missing argument version.' in result.output)
            self.assertEqual(result.exit_code, 2)

    def test_version_must_be_semantic_version(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(release, ['foo'])

            self.assertTrue('Error: Invalid value: foo is not a semantic version' in result.output)
            self.assertEqual(result.exit_code, 2)
