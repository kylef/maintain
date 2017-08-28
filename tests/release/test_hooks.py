import unittest
import subprocess

from maintain.release.hooks import HookReleaser


class HookReleaseTests(unittest.TestCase):
    def test_calls_pre_bump_hooks(self):
        releaser = HookReleaser({
            'bump': {
                'pre': ['exit 1']
            }
        })

        with self.assertRaises(subprocess.CalledProcessError):
            releaser.pre_bump(None)

    def test_calls_post_bump_hooks(self):
        releaser = HookReleaser({
            'bump': {
                'post': ['exit 1']
            }
        })

        with self.assertRaises(subprocess.CalledProcessError):
            releaser.post_bump(None)

    def test_calls_pre_release_hooks(self):
        releaser = HookReleaser({
            'publish': {
                'pre': ['exit 1']
            }
        })

        with self.assertRaises(subprocess.CalledProcessError):
            releaser.pre_release(None)

    def test_calls_post_release_hooks(self):
        releaser = HookReleaser({
            'publish': {
                'post': ['exit 1']
            }
        })

        with self.assertRaises(subprocess.CalledProcessError):
            releaser.post_release(None)
