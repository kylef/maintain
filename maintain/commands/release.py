import os
import sys
import logging

import click
from click.exceptions import MissingParameter
import yaml
from semantic_version import Version

from maintain.release.aggregate import AggregateReleaser
from maintain.release.git_releaser import GitReleaser
from maintain.release.github import GitHubReleaser


logger = logging.getLogger('maintain.release')


@click.command()
@click.argument('version', required=False)
@click.option('--dry-run/--no-dry-run', default=False)
@click.option('--bump/--no-bump', default=True)
@click.option('--pull-request/--no-pull-request', default=False)
@click.option('--verbose/--no-verbose', default=False)
def release(version, dry_run, bump, pull_request, verbose):
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if verbose:
        logger.setLevel(logging.DEBUG)

    if os.path.exists('.maintain.yml'):
        with open('.maintain.yml') as fp:
            config = yaml.load(fp.read())
    else:
        config = {}

    releaser = AggregateReleaser(config.get('release', {}))

    git_releasers = filter(lambda releaser: isinstance(releaser, GitReleaser), releaser.releasers)
    github_releasers = filter(lambda releaser: isinstance(releaser, GitHubReleaser), releaser.releasers)

    try:
        git_releaser = next(git_releasers)
    except StopIteration:
        git_releaser = None
    except TypeError:
        if len(git_releasers) > 0:
            git_releaser = git_releasers[0]
        else:
            git_releaser = None

    try:
        github_releaser = next(github_releasers)
    except StopIteration:
        github_releaser = None
    except TypeError:
        if len(github_releasers) > 0:
            github_releaser = github_releasers[0]
        else:
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
        logger.info('Bumping {}'.format(version))

        ref = git_releaser.repo.refs.master
        if pull_request:
            branch = 'release-{}'.format(version)
            ref = git_releaser.repo.create_head(branch, git_releaser.repo.head)
            git_releaser.repo.head.set_reference(ref)

        releaser.bump(version)

        if not dry_run:
            if git_releaser.has_origin():
                git_releaser.repo.remotes.origin.push(ref)

            if pull_request:
                github_releaser.create_pull_request(version)

    if not dry_run and not pull_request:
        logger.info('Releasing {}'.format(version))
        releaser.release(version)


def bump_version(version, bump):
    if version.prerelease or version.build:
        print('Current version {} contains prerelease or build. ' +
              'Bumping is not supported.'.format(version))
        exit(1)

    return getattr(version, 'next_{}'.format(bump))()
