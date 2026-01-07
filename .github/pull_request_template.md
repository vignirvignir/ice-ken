<!--
Please use a Conventional Commit–style PR title. Required format:

  <type>(<scope>): <description>

Types: feat | fix | docs | style | refactor | perf | test | build | ci | chore | revert
Scope: short area name (e.g., kennitala, tests, ci)

Examples:
- ci(release): avoid detached HEAD and use conventional commit parser
- fix(kennitala): handle 2000s century indicator in relaxed mode
-->

## Summary

Describe what this PR changes and why.

## Changes
- 
- 

## Checklist
- [ ] PR title follows Conventional Commits with a scope (e.g., `ci(release): ...`)
- [ ] Tests pass (`pytest`)
- [ ] Adds/updates tests where appropriate
- [ ] Updates docs if behavior or public API changed
- [ ] No manual version bump (semantic-release handles versioning)

## Related
Link related issues or discussions.

## Notes
- The release workflow requires a valid Conventional Commit title on PRs.
- On merge to main, semantic-release will compute the next version and publish.
