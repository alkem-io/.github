# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the owners of this repository before making a change.

Please note we have a ![code of conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

For security, we only allow for [signed commits](https://help.github.com/en/github/authenticating-to-github/signing-commits) to be merged into master. This is to prevent [git spoofing](https://cybermundus.com/post/git-spoofing/). If you are new to signing your commits, don't worry! For some helpful starting points you can look here: [commit signing in github](https://help.github.com/en/github/authenticating-to-github/signing-commits), [Signing your work](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work), and [Qubes-OS guide to PGP and signed commits](https://www.qubes-os.org/doc/code-signing/).

## Developer Certificate of Origin

All contributions are certified under the [Developer Certificate of Origin v1.1](https://developercertificate.org/) (DCO).
Every commit must carry a `Signed-off-by` trailer matching your Git identity:

    git commit -s -m "your commit message"

which appends a trailer of the form:

    Signed-off-by: Your Name <your@email.com>

If you already created commits without a sign-off, fix them without losing your work:

    git rebase --signoff HEAD~<number of commits>
    git push --force-with-lease

A `DCO` status check enforces this on every pull request. Sign-off complements the mandatory
commit signing above: signing cryptographically authenticates *who* made the commit, while the
sign-off declares that you have the *right* to submit the work under the project's licence.

## Pull Request Process
We use the [Fork&Pull](https://guides.github.com/activities/forking/) method for contributing. 

1. Ensure any install or build dependencies are removed before the end of the layer when doing a
   build.
2. Update the README.md with details of changes to the interface, this includes new environment
   variables, exposed ports, useful file locations and container parameters.
3. Increase the version numbers in any examples files and the README.md to the new version that this
   Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
4. You may merge the Pull Request in once you have the sign-off of one other developers, or if you
   do not have permission to do that, you may request the reviewer to merge it for you.


