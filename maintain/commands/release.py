import os
import subprocess

import click
from click.exceptions import MissingParameter
import yaml
from semantic_version import Version

from maintain.release.aggregate import AggregateReleaser
from maintain.release.git_releaser import GitReleaser
from maintain.release.github import GitHubReleaser


@click.command()
@click.argument('version', required=False)
@click.option('--dry-run/--no-dry-run', default=False)
@click.option('--bump/--no-bump', default=True)
@click.option('--pull-request/--no-pull-request', default=False)
def release(version, dry_run, bump, pull_request):
    if os.path.exists('.maintain.yml'):
        with open('.maintain.yml') as fp:
            config = yaml.load(fp.read())
    else:
        config = {}

    releaser = AggregateReleaser()

    try:
        git_releaser = next(filter(lambda releaser: isinstance(releaser, GitReleaser), releaser.releasers))
    except StopIteration:
        git_releaser = None

    try:
        github_releaser = next(filter(lambda releaser: isinstance(releaser, GitHubReleaser), releaser.releasers))
    except StopIteration:
        github_releaser = None

    if pull_request and not github_releaser:
        raise Exception('Used --pull-request and no GitHub remote')

    if not version and bump:
        raise MissingParameter(param_hint='version', param_type='argument')
    elif version == 'semver':
        version = releaser.determine_next_version()
        if not version:
            raise Exception('Could not determine the next semantic version.')
    elif version in ('major', 'minor', 'patch'):
        if bump:
            version = bump_version(releaser.determine_current_version(), version)
        else:
            releaser.determine_current_version()
    else:
        try:
            version = Version(version)
        except ValueError:
            raise click.BadParameter('{} is not a semantic version'.format(version))

    if not bump:
        current_version = releaser.determine_current_version()
        if current_version != version:
            click.echo('--no-bump was used, however the supplied version ' +
                       'is not equal to current version {} != {}'.format(current_version, version))
            exit(1)

    if bump:
        ref = git_releaser.repo.refs.master
        if pull_request:
            branch = 'release-{}'.format(version)
            ref = git_releaser.repo.create_head(branch, git_releaser.repo.head)
            git_releaser.repo.head.set_reference(ref)

        execute_hooks('bump', 'pre', config)
        releaser.bump(version)
        execute_hooks('bump', 'post', config)

        if not dry_run:
            if git_releaser.has_origin():
                git_releaser.repo.remotes.origin.push(ref)

            if pull_request:
                github_releaser.create_pull_request(version)

    if not dry_run and not pull_request:
        execute_hooks('publish', 'pre', config)
        releaser.release(version)
        execute_hooks('publish', 'post', config)


def bump_version(version, bump):
    if version.prerelease or version.build:
        print('Current version {} contains prerelease or build. ' +
              'Bumping is not supported.'.format(version))
        exit(1)

    return getattr(version, 'next_{}'.format(bump))()




def execute_hooks(phase, action, config):
    release_config = config.get('release', {})
    phase_config = release_config.get(phase, {})
    hooks = phase_config.get(action, [])

    if len(hooks) > 0:
        click.echo('Running {} {} hooks'.format(phase, action))

        for hook in hooks:
            click.echo('- ' + hook)
            subprocess.check_output(hook, shell=True)
