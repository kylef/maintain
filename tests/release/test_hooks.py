import unittest
import subprocess

from maintain.release.hooks import HookReleaser
from ..utils import temp_directory


class HookReleaseTests(unittest.TestCase):
    def test_calls_pre_bump_hooks(self):
        releaser = HookReleaser({
            'bump': {
                'pre': ['exit 1']
            }
        })

        with self.assertRaises(subprocess.CalledProcessError):
            releaser.pre_bump('1.0.0')

    def test_calls_post_bump_hooks(self):
        releaser = HookReleaser({
            'bump': {
                'post': ['exit 1']
            }
        })

        with self.assertRaises(subprocess.CalledProcessError):
            releaser.post_bump('1.0.0')

    def test_calls_pre_release_hooks(self):
        releaser = HookReleaser({
            'publish': {
                'pre': ['exit 1']
            }
        })

        with self.assertRaises(subprocess.CalledProcessError):
            releaser.pre_release('1.0.0')

    def test_calls_post_release_hooks(self):
        releaser = HookReleaser({
            'publish': {
                'post': ['exit 1']
            }
        })

        with self.assertRaises(subprocess.CalledProcessError):
            releaser.post_release('1.0.0')

    def test_passes_version_environment_to_hook(self):
        releaser = HookReleaser({
            'bump': {
                'pre': ['echo $VERSION > output']
            }
        })

        with temp_directory():
            releaser.pre_bump('1.0.0')

            with open('output') as fp:
                self.assertEqual(fp.read(), '1.0.0\n')
