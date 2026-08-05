# CLA → DCO migration notice

As of the cut-over date (**TBD — finalized at enforcement switch**), the
Alkemio organisation enforces the
[Developer Certificate of Origin v1.1](https://developercertificate.org/)
(DCO) on every pull request, replacing the previous Contributor License
Agreement process operated through cla-assistant.io
(tracking story: [alkem-io/infrastructure-operations#2186](https://github.com/alkem-io/infrastructure-operations/issues/2186)).

## What changed

- Every commit must carry a `Signed-off-by` trailer matching the author's
  Git identity (`git commit -s`). A required `DCO` status check enforces
  this on all pull requests, alongside the existing mandatory commit
  signing.
- The [CLA](CLA.md) is retired for new contributions. It remains binding
  for contributions made while it was in force.

## Historical signature archive

The complete cla-assistant signature export — one CSV per connected
repository plus a SHA-256 manifest — is preserved in the private
`alkem-io/infrastructure-operations` repository under
`legal/cla-migration/`. This public notice intentionally references the
archive by path only; per-file row counts and checksums may be mirrored
here after the archive is verified, never the CSV contents.

## Why DCO

The cla-assistant tooling is effectively unmaintained. DCO is the standard
used by the Linux kernel, Kubernetes, and most CNCF projects: the sign-off
is embedded in the signed Git object itself, making it tamper-evident and
permanently tied to the commit history — a stronger record than an external
service's OAuth session, given the organisation's mandatory commit-signing
policy.

## How to comply

See the [DCO section of CONTRIBUTING](CONTRIBUTING.md#developer-certificate-of-origin)
for `git commit -s`, the trailer format, and fixing existing commits with
`git rebase --signoff`.
