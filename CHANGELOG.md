# CHANGELOG


## v2.0.1 (2026-03-28)

### Bug Fixes

- **ci**: Use version tag for pypa/gh-action-pypi-publish
  ([`7d1637b`](https://github.com/vignirvignir/ice-ken/commit/7d1637bc02cb88d6a7e74b7a064949cd525c224b))

Docker-based actions require image tags, not commit SHAs. The Docker registry has no image for the
  commit SHA, causing manifest unknown error.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>


## v2.0.0 (2026-03-27)

### Bug Fixes

- **examples**: Add example output for the usage file
  ([`2d35a00`](https://github.com/vignirvignir/ice-ken/commit/2d35a009a1d62711842ef48700ab2dec7a5c54b8))

- **kennitala**: Add max-iteration guard to _build_kennitala loop
  ([`af59afe`](https://github.com/vignirvignir/ice-ken/commit/af59afe6f823d768f5d82623e58977dceafb6664))

Replace unbounded while-True with a capped for-loop (1000 attempts) that raises RuntimeError on
  exhaustion, preventing a theoretical infinite loop.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Cap generate_batch at 100k and document limitations
  ([`f6a1655`](https://github.com/vignirvignir/ice-ken/commit/f6a1655574f15ab380306f12f46148fdfa7b118a))

Add upper bound on count to prevent OOM DoS. Document that duplicates are possible (~73 unique IDs
  per date) and that generation uses a non-cryptographic PRNG unsuitable for security tokens.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Derive __version__ from package metadata instead of hardcoded value
  ([`51eb147`](https://github.com/vignirvignir/ice-ken/commit/51eb14747f1921011f428d4ba328383eefba9295))

Replaces the stale hardcoded "0.1.0" with importlib.metadata lookup so ice_ken.__version__ always
  matches the installed package version.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Mask PII in ParsedKennitala repr to prevent log leakage
  ([`61411f3`](https://github.com/vignirvignir/ice-ken/commit/61411f3e91cdddeaaa3651833e88849db9e7996d))

Override __repr__ to display masked formatted value instead of full digits, preventing accidental
  exposure of national IDs in logs, tracebacks, and debug output. Full data remains accessible via
  .digits and .formatted attributes.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Raise TypeError in normalize() for non-string input
  ([`fd0b806`](https://github.com/vignirvignir/ice-ken/commit/fd0b8065e092d34f34b25e1495f6e9c85dbe2365))

Provides a clear error message instead of an unhelpful iteration TypeError when callers accidentally
  pass None, int, or other non-str values.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Raise ValueError when both target_date and birth_date are passed
  ([`958c662`](https://github.com/vignirvignir/ice-ken/commit/958c66253aa86c58e0f169aafdd04f6b8fa356b5))

Prevents silent precedence confusion in generate_kennitala and generate_batch where target_date
  would silently win over birth_date.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Reject non-integer visible_tail in mask()
  ([`4956065`](https://github.com/vignirvignir/ice-ken/commit/49560653ed81c638bc1c17087bebfe9272362cd9))

Add isinstance check so float values like 3.5 raise a clear ValueError instead of an internal
  TypeError from slice operations.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Reject unexpected characters in normalize()
  ([`407e4ab`](https://github.com/vignirvignir/ice-ken/commit/407e4aba6708d24a5c8fc143764732ea160357a4))

normalize() now raises ValueError on characters other than ASCII digits, hyphens, and whitespace.
  This prevents silent data corruption from mixed-content strings (e.g. 'Phone: 123-456-7890'
  becoming '1234567890'). Predicate functions (is_valid, is_company, is_personal, is_dataset_id)
  catch the error and return False.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Restrict normalize() to ASCII digits only
  ([`8df9871`](https://github.com/vignirvignir/ice-ken/commit/8df9871f2dcf8a49de3a0243bc1b8a6002ea7d5b))

Replace ch.isdigit() with '0' <= ch <= '9' to reject Unicode fullwidth digits, superscripts, and
  Arabic-Indic numerals. The old behavior could crash is_valid() with unhandled ValueError on
  superscript digits or silently produce non-canonical digit strings from fullwidth input.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Use dynamic end date for random generation ranges
  ([`6914547`](https://github.com/vignirvignir/ice-ken/commit/6914547b957ecef9537cd594e8d1141324e9fe9b))

Replace hardcoded 2025-12-31 end dates with date.today().year so generated IDs stay current as the
  calendar advances.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Validate dates in is_company/is_personal and fix mask edge cases
  ([`0a361a3`](https://github.com/vignirvignir/ice-ken/commit/0a361a3b3fadea50e4aa81ffd2efc2d6c37393e0))

is_company and is_personal now verify the date and century indicator via relaxed validation,
  rejecting structurally invalid kennitalas (e.g. day=00). mask() now bounds-checks visible_tail
  (0–10) and correctly handles visible_tail=10 by returning the full formatted kennitala.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **loaders**: Add --mask CLI flag to redact kennitalas in output
  ([`d3dde3d`](https://github.com/vignirvignir/ice-ken/commit/d3dde3d26cfcbe4ec31bea5a0c9c61a4e38277a1))

Prevents accidental PII exposure when piping loader output to logs or shared files. Applies mask()
  to the Kennitala field of each record.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **loaders**: Emit warning when defusedxml is not installed
  ([`0d23134`](https://github.com/vignirvignir/ice-ken/commit/0d23134bda97cb78c274862d6b280ff6cc01b03a))

Replace misleading safety comment with a runtime ImportWarning and accurate documentation that
  stdlib XML parsing is vulnerable to entity expansion (billion laughs) DoS. External entities (XXE)
  are still blocked by Python 3.x.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **loaders**: Fix XML parser fallback compatibility with Python 3.9
  ([`dbdb4f0`](https://github.com/vignirvignir/ice-ken/commit/dbdb4f0af0ba886a975ce5cb12a39843f94254fa))

The parser.entity attribute is readonly on Python 3.9, causing AttributeError. Use ET.fromstring
  directly as the stdlib C-accelerated XMLParser already does not resolve external entities.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **loaders**: Harden XML parsing against entity expansion attacks
  ([`c90abde`](https://github.com/vignirvignir/ice-ken/commit/c90abdea74d1f8f3d5dfed55272426252a75819c))

Use defusedxml when available, falling back to a hardened stdlib XMLParser that disables external
  entity resolution.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### Chores

- **kennitala**: Add gitignore patterns for PII-bearing file types
  ([`d347ee5`](https://github.com/vignirvignir/ice-ken/commit/d347ee5a52f2fed16108fe7b8690364957a4283a))

Prevent accidental commits of database dumps, spreadsheets, and generated JSON files that may
  contain real kennitalas.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Add py.typed marker, __all__, and modernize type hints
  ([`7a2bd73`](https://github.com/vignirvignir/ice-ken/commit/7a2bd735b465b10d5fb1a1167896eb6f3cc85218))

- Add py.typed marker so mypy/pyright consumers get type checking (#16) - Add __all__ to
  kennitala.py to gate the public API (#17) - Replace typing.Optional/List/Dict/Union with PEP
  604/585 syntax in both kennitala.py and loaders.py (#18) - Remove unused imports (dataclass,
  asdict) from loaders.py - Include py.typed in package-data via pyproject.toml

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **license**: Switch from GPL-3.0 to MIT license
  ([`7d809e3`](https://github.com/vignirvignir/ice-ken/commit/7d809e3f4ad8df3623e794c7704606e091920ec1))

Replace GNU GPL v3 with MIT license across LICENSE file, pyproject.toml, and README.md.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### Continuous Integration

- **release**: Include environment claim for OIDC (prod)
  ([`14b5965`](https://github.com/vignirvignir/ice-ken/commit/14b5965753bf7d99cb4caceccea0d2f602ad0fe6))

- **workflows**: Add security comment and reduce permissions on semantic-pr
  ([`8506590`](https://github.com/vignirvignir/ice-ken/commit/8506590bf6718e586fa53e1c140658a6e70379d4))

Document that pull_request_target must never check out fork code. Remove unnecessary checks:write
  permission.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **workflows**: Pin GitHub Actions to commit SHAs and bound dependency versions
  ([`a552e97`](https://github.com/vignirvignir/ice-ken/commit/a552e97638ceabc19b987dbd55d270509cbd19f2))

Pin all GitHub Actions to immutable commit SHAs to prevent supply chain attacks via compromised
  mutable tags. Bound CI and release dependency versions (pytest, python-semantic-release, build) to
  major ranges.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### Documentation

- **claude**: Add CLAUDE.md for Claude Code context
  ([`133fe4a`](https://github.com/vignirvignir/ice-ken/commit/133fe4ab144e38a7d7cf55655521aa02aea98b54))

Provides commands, architecture overview, domain rules, and commit conventions so future Claude Code
  instances can be productive immediately in this repo.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Add 2026 checksum policy warnings to is_valid and parse
  ([`2fb1c80`](https://github.com/vignirvignir/ice-ken/commit/2fb1c80609be83c212b7563a7f9ed1b4cddbddce))

Surface the Feb 2026 policy change prominently in the docstrings so callers know to pass
  enforce_checksum=False for post-2026 IDs.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Fix incorrect positional args and use target_date in examples
  ([`1023168`](https://github.com/vignirvignir/ice-ken/commit/10231688abd1c8b3722b4af0c7572d8fe2003c51))

Fix generate_personal(False) and generate_company(False) in docs — these are keyword-only params
  that would raise TypeError. Update README batch example to use target_date instead of deprecated
  birth_date.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Improve README and metadata for LLM discoverability
  ([`48a2c47`](https://github.com/vignirvignir/ice-ken/commit/48a2c47b883e19dd879c63660e05ce1f955f602e))

Add rich opening description with Icelandic terminology (kennitölur, Þjóðskrá), international
  equivalents (SSN, personnummer), and use-case framing (KYC/AML, government registries). Add "Why
  ice-ken?" section highlighting key capabilities. Update pyproject.toml description and keywords
  with additional search terms.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **readme**: Rewrite for clarity and usability
  ([`62a4271`](https://github.com/vignirvignir/ice-ken/commit/62a427199bb6b4090bb2c388f68f3124be69a127))

### Features

- **examples**: Add comprehensive usage and loader examples
  ([`138eb76`](https://github.com/vignirvignir/ice-ken/commit/138eb767caa26ed8e6c7a8ed816ab11654e2c4e5))

- **kennitala**: Change enforce_checksum default to False for validation
  ([`02b754b`](https://github.com/vignirvignir/ice-ken/commit/02b754b805f839c9c12a6e9b5e10cd23b37050b4))

BREAKING CHANGE: is_valid(), parse(), and get_birth_date() now default to enforce_checksum=False
  (relaxed validation). Since Feb 18, 2026, Registers Iceland issues kennitalas without valid
  Modulus 11 checksums, making the old strict default actively harmful for production systems.

Generation functions retain enforce_checksum=True as default since producing checksum-valid test
  data is still the common case.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Improve generation API with unified helpers and batch support
  ([`4074ce0`](https://github.com/vignirvignir/ice-ken/commit/4074ce0b01687f4ba1044d98a8f23bc51073da05))

Refactor generation to eliminate duplicated logic via _build_kennitala(), add birth_date/reg_date
  params to generate_personal/generate_company, introduce generate_kennitala() unified entry point
  and generate_batch() for bulk generation. All generation functions are now exported. Includes
  comprehensive tests and README documentation.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### Refactoring

- **kennitala**: Rename birth_date to target_date in unified generators
  ([`d55f0f1`](https://github.com/vignirvignir/ice-ken/commit/d55f0f1cf3adf35abe1643258287e2eef18a1db2))

generate_kennitala and generate_batch now use target_date as the primary parameter name, which is
  accurate for both personal (birth) and company (registration) IDs. birth_date is kept as a
  deprecated alias for backward compatibility.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### Testing

- **kennitala**: Add tests for is_personal/is_company validation and mask edge cases
  ([`9c0f0ce`](https://github.com/vignirvignir/ice-ken/commit/9c0f0ce48b5664dd6d74d60426536ab66f36f3b2))

Cover invalid dates, invalid century indicators, visible_tail=10, and out-of-range visible_tail
  values.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **kennitala**: Close test gaps #10-#14 from code review
  ([`37ced99`](https://github.com/vignirvignir/ice-ken/commit/37ced99c88a55da8643805bacb0ef8e1f218f689))

- Add get_birth_date invalid input tests (bad length, bad checksum, invalid date) - Expand
  test_loader.py: wrong root element, empty file, missing fields, nil attributes, invalid
  kennitalas, file not found, malformed XML, and CLI main() with both stdout and file output -
  Remove duplicated checksum/century helpers from test_properties.py and import from the module
  directly; remove associated typo (AssertionError)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### Breaking Changes

- **kennitala**: Is_valid(), parse(), and get_birth_date() now default to enforce_checksum=False
  (relaxed validation). Since Feb 18, 2026, Registers Iceland issues kennitalas without valid
  Modulus 11 checksums, making the old strict default actively harmful for production systems.


## v1.1.0 (2026-01-07)

### Chores

- **ci**: Update permissions in semantic PR workflow to enhance security
  ([`7af0f67`](https://github.com/vignirvignir/ice-ken/commit/7af0f676d0236bfea6fafc308ace30daa707e1ca))

- **ci**: Update semantic PR workflow to use pull_request event
  ([`c88339a`](https://github.com/vignirvignir/ice-ken/commit/c88339a0588d783044e840f2d08a0007bdcf2699))

- **ci**: Update semantic PR workflow to use pull_request_target event and add permissions
  ([`550e14e`](https://github.com/vignirvignir/ice-ken/commit/550e14e2f38abac3f7c91e664517da7cf3822c9c))

### Continuous Integration

- **env**: Use 'prod' environment for release and testpypi OIDC claims
  ([`0a217de`](https://github.com/vignirvignir/ice-ken/commit/0a217de9d3b2fb991374708f4cfdb3ef308b08a9))

- **release**: Avoid detached HEAD and use conventional commit parser
  ([`5e77950`](https://github.com/vignirvignir/ice-ken/commit/5e77950f1dc8548fb3972c07514d43b86eab1755))

- **release**: Make publishing manual-only via workflow_dispatch
  ([`75b8d11`](https://github.com/vignirvignir/ice-ken/commit/75b8d116eabc5278a813448101b8cd32f28f4289))

- **release**: Run on push or manual dispatch; skip on PRs
  ([`98dce65`](https://github.com/vignirvignir/ice-ken/commit/98dce655fd590a8579d5f033b08e282c987a7363))

- **release-pr**: Add prepare_release_pr job and tag-on-merge flow; stop direct push to main
  ([`13183ba`](https://github.com/vignirvignir/ice-ken/commit/13183ba56a30f71396583fe93cc19c0eb28315c8))

- **testpypi**: Add environment 'production' for OIDC Trusted Publisher
  ([`3a781f9`](https://github.com/vignirvignir/ice-ken/commit/3a781f967260d38ecd023eb13ca29af7f9430c04))

- **testpypi**: Checkout PR head SHA to avoid invalid 9/merge ref
  ([`a2b3d39`](https://github.com/vignirvignir/ice-ken/commit/a2b3d39e217c9f71a392b4ec36a15acd7bde1a87))

- **testpypi**: Grant contents:read alongside id-token for publish action
  ([`035333f`](https://github.com/vignirvignir/ice-ken/commit/035333f95669d41cda0296cda3e76e4ed23db808))

- **testpypi**: Remove environment to match publisher without environment
  ([`632d11d`](https://github.com/vignirvignir/ice-ken/commit/632d11d71d0a0b21a79b19d24337c1f7ba8cf89a))

- **testpypi**: Retrigger workflow to validate publisher
  ([`d70f42a`](https://github.com/vignirvignir/ice-ken/commit/d70f42a93215637e73f1b72424ce05ce9789ae11))

### Documentation

- **pr-template**: Add PR template to enforce Conventional Commit titles
  ([`8ff4e4c`](https://github.com/vignirvignir/ice-ken/commit/8ff4e4cb06fbe89a45871e4d92c931d0e30c810c))


## v1.0.2 (2026-01-07)

### Bug Fixes

- **release**: Standardize environment name to 'Production' in workflow
  ([`58bd743`](https://github.com/vignirvignir/ice-ken/commit/58bd743c7ced9b578fdb8f73ffe4f5fa1fb3c5a3))

- **release**: Standardize environment name to lowercase in workflow
  ([`9a18b29`](https://github.com/vignirvignir/ice-ken/commit/9a18b29b313157ea6a2409b25cda725b1460884e))

### Chores

- **ci**: Fix semantic PR permissions and inputs
  ([`ba0283e`](https://github.com/vignirvignir/ice-ken/commit/ba0283e8dedbba770cbb2cc5b44bd935ed475c32))

### Continuous Integration

- **release**: Add Production environment for PyPI trusted publishing
  ([`f9a21f1`](https://github.com/vignirvignir/ice-ken/commit/f9a21f1069ec9534de786c1c0a6ebdac0fa5552f))

- **release**: Remove environment constraint for OIDC trusted publishing
  ([`a81cc14`](https://github.com/vignirvignir/ice-ken/commit/a81cc14a21646efc030dc3d939bd264dbb9dcd6f))

- **semantic-pr**: Grant checks and pull-requests write permissions to fix integration access
  ([`1e73262`](https://github.com/vignirvignir/ice-ken/commit/1e73262c3650a276ea65d93d9550234a5658cef1))

### Features

- **tests**: Add tests for personal and company kennitala generation functions
  ([`0eb9314`](https://github.com/vignirvignir/ice-ken/commit/0eb93148945ebf0810cf6007d52b45151748db8d))


## v1.0.1 (2026-01-07)

### Bug Fixes

- **release**: Add GH_TOKEN to environment variables for semantic-release steps
  ([`5d47583`](https://github.com/vignirvignir/ice-ken/commit/5d47583fc482cfd6a3c0f943c11ba4f806ae9221))


## v1.0.0 (2026-01-07)

### Bug Fixes

- **commitlint**: Increase header max length from 72 to 120 characters
  ([`6e4cdef`](https://github.com/vignirvignir/ice-ken/commit/6e4cdef49cff2857bf1c4dddcc6422c3b016904d))

- **types**: Replace Python 3.10+ union syntax for Python 3.9 compatibility
  ([`50b4eb6`](https://github.com/vignirvignir/ice-ken/commit/50b4eb6a54fea1f217ae29378be0d76c9316048a))

- Change 'int | None' to 'Optional[int]' in test_properties.py - Change 'str | Path' to 'Union[str,
  Path]' in loaders.py - Ensures compatibility with Python 3.9+ requirement in pyproject.toml

### Chores

- **ci**: Enhance CI workflows with improved concurrency and caching settings
  ([`6645d51`](https://github.com/vignirvignir/ice-ken/commit/6645d5179242f1fea4329eb83e78e3a2c4cb73de))

### Documentation

- **commit-message**: Update commit message guidelines for clarity
  ([`ffdc9e1`](https://github.com/vignirvignir/ice-ken/commit/ffdc9e1763c095cbb76c1461573967a613db18bf))

### Features

- **kennitala**: Add comprehensive handling for Icelandic national IDs
  ([`e6be123`](https://github.com/vignirvignir/ice-ken/commit/e6be12317d543e1f04da0a295d0123b1c1a47c16))

- Introduced detailed documentation for XML data files and system identification numbers. - Added
  vocabulary for Icelandic-English technical terms related to national identification systems. -
  Implemented XML parsing and validation for synthetic datasets from Registers Iceland. - Enhanced
  kennitala utilities for normalization, validation, formatting, and masking. - Developed tests for
  kennitala functionalities, including fuzz testing for robustness. - Created loaders for handling
  XML data and converting it to validated JSON format.

- **license**: Add project copyright and contributor guidelines
  ([`53b2ca6`](https://github.com/vignirvignir/ice-ken/commit/53b2ca600c38bdb744baedc70b642bd5a5883c09))

- Add project-specific copyright notice to LICENSE file - Add comprehensive Contributing section to
  README - Encourage community contributions while protecting GPL requirements
