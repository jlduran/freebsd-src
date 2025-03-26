FreeBSD maintainer's guide to blocklist
=======================================

These instructions describe the blocklist vendor import procedure,
following the Committer's Guide
(https://docs.freebsd.org/en/articles/committers-guide/#vendor-import-git).

> [!NOTE]
> This guide follows the convention that the `freebsd` remote is
> pointing to gitrepo.FreeBSD.org/src.git.

1.  Grab our top level directory:

        freebsd=$(git rev-parse --show-toplevel)

2.  Create a Git worktree under a temporary directory:

        worktree=$(mktemp -d -t blocklist)
        git worktree add ${worktree} vendor/blocklist

3.  Clone the blocklist repo (https://github.com/zoulasc/blocklist.git):

        blocklist_repo=$(mktemp -d -t blocklist-repo)
        git clone https://github.com/zoulasc/blocklist.git ${blocklist_repo}
        version=$(git rev-parse --short --prefix ${blocklist_repo} HEAD)

4.  Copy to the vendor branch using rsync (net/rsync):

        rsync -va --del --exclude=".git" ${blocklist_repo}/ ${worktree}

5.  Take care of added/deleted files:

        cd ${worktree}
        git add -A ${worktree}
        git status
        git diff --staged

6.  Commit:

        git commit -m "Vendor import of blocklist (${version})"

7.  Tag:

        git tag -a -m "Tag blocklist ${version}" vendor/blocklist/${version}

    At this point, the vendor branch can be pushed to the FreeBSD repo
    via:

        git push --follow-tags freebsd vendor/blocklist

8.  Merge from the vendor branch:

        cd ${freebsd}
        git subtree merge -P contrib/blocklist vendor/blocklist

    Some files may have been deleted from FreeBSD's copy of blocklist.
    When git prompts for these deleted files during the merge, choose 'd'
    (leaving them deleted).

9.  Resolve conflicts.

10. Diff against the vendor branch:

        git diff --diff-filter=M vendor/blocklist/${version} HEAD:contrib/blocklist

    Review the diff for any unexpected changes.

11. Run the local changes scripts:

        cd contrib/blocklist
        sh ./freebsd-changes.sh
        sh ./freebsd-rename.sh

12. If source files have been added or removed, update the appropriate
    makefiles to reflect changes in the vendor's Makefile.in.

13. Build and install world, reboot, test.  Pay particular attention
    to the ftpd(8) and sshd(8) integration.

14. Commit.

15. Cleanup:

        rm -fr ${blocklist_repo} ${worktree}
        git worktree prune
