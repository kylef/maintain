DEFAULT_BRANCHES = set(["master", "main"])


def get_default_branch(repo):
    default_branches = [branch for branch in DEFAULT_BRANCHES if branch in repo.heads]

    if len(default_branches) > 1:
        branches = ", ".join(sorted(default_branches))
        raise Exception(f"Found multiple default branches, ambgious: {branches}")
    elif len(default_branches) == 0:
        raise Exception("Could not find a default branch")

    return default_branches[0]
