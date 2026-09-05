# CHANGELOG

<!-- version list -->

## v0.5.0 (2026-09-05)

### Build System

- Add py.typed marker
  ([`9fdef21`](https://github.com/djachenko/justin_utils/commit/9fdef214f4291865eaa40800ffa2889fa4941cc8))

### Chores

- Ignore the _claude symlink
  ([`5eac279`](https://github.com/djachenko/justin_utils/commit/5eac2798c7399501165d805bf2ee9e74bc02ef9e))

### Code Style

- Collapse the parametrize decorator
  ([`1ba68c3`](https://github.com/djachenko/justin_utils/commit/1ba68c3aa1d9d3175528b13f1c981884b1525afc))

### Features

- Report deserialization failures with DictableError
  ([`e128ff4`](https://github.com/djachenko/justin_utils/commit/e128ff40e00ee732799d423c5fd4a3cc7d240265))

### Refactoring

- Replace lambda defaults with named callables in pylinq
  ([`cd2bc3f`](https://github.com/djachenko/justin_utils/commit/cd2bc3f40c0313dc84ac9d4487049afe29aae898))

- Stop assuming every Dictable is a dataclass
  ([`2e6366e`](https://github.com/djachenko/justin_utils/commit/2e6366ee6cb05502eaff1950f70330551dd284f4))

### Testing

- Accept the windows error for reading a directory
  ([`ef4bcf3`](https://github.com/djachenko/justin_utils/commit/ef4bcf3b3333e15d7f883022526f435b031eff1a))

- Support binary files in the conftest file tree
  ([`9d2f49f`](https://github.com/djachenko/justin_utils/commit/9d2f49f6a50ceec9db1805ab9a5444ef2c6ca989))


## v0.4.1 (2026-09-05)

### Bug Fixes

- Raise AssertionError instead of assert False
  ([`6e0dc14`](https://github.com/djachenko/justin_utils/commit/6e0dc148b1bab63baa1266f1ea7dccdc2208275b))

- Raise meaningful exceptions instead of AssertionError
  ([`c6a6cd8`](https://github.com/djachenko/justin_utils/commit/c6a6cd893b6406cfd9e00d894d688b5df42065c4))

- Return None for a RAF with a truncated header
  ([`d347f81`](https://github.com/djachenko/justin_utils/commit/d347f814259b4fef9834a2ddc25e6c2e249d20c4))

### Chores

- Configure ruff lint rules and line length
  ([`5bde5ef`](https://github.com/djachenko/justin_utils/commit/5bde5ef93df21a3f0289c7f5a8596b0dd9fdbc0e))

### Code Style

- Apply ruff format
  ([`80c5a39`](https://github.com/djachenko/justin_utils/commit/80c5a39f2058757fa1670606f0d32af1885d8876))

- Drop the formatter, keep the linter
  ([`642e030`](https://github.com/djachenko/justin_utils/commit/642e0301081a95b09219ef63df93c858cdafbd6b))

- Preserve author quote style and keep exploded call sites
  ([`0d0de99`](https://github.com/djachenko/justin_utils/commit/0d0de99e8aafb218386c49f2b55b0242e58fe2e5))

### Refactoring

- Call the classmethod on type(self), not the instance
  ([`21cce05`](https://github.com/djachenko/justin_utils/commit/21cce05fff1e29e2e32a2152aaae5a60bf7fcfd4))

- Drop the decorative ABC from Singleton
  ([`70d5acc`](https://github.com/djachenko/justin_utils/commit/70d5accb93c80771da6a8af97fcb9e6df34290de))

- Drop two noqa directives by fixing their cause
  ([`84f88ca`](https://github.com/djachenko/justin_utils/commit/84f88cade2c8210fb056b27d8bc111347d73bc33))

- Fix ruff lint findings
  ([`517c6a7`](https://github.com/djachenko/justin_utils/commit/517c6a7e7acf1c868190d6d8cb9d162038458afc))

- Remove the unused TypeVar from singleton
  ([`07cb39c`](https://github.com/djachenko/justin_utils/commit/07cb39ce74255f0911e19e87df30460143e030e6))

- Return Self from constructing classmethods
  ([`9b19301`](https://github.com/djachenko/justin_utils/commit/9b193013045dc74c78a6d8e21870ab29a3792969))


## v0.4.0 (2026-08-19)

### Features

- Rewrite exif parsing with container abstraction and RAF support
  ([`556ac3c`](https://github.com/djachenko/justin_utils/commit/556ac3c390d745ff238df2211777ba99f5ae153e))

### Refactoring

- Make RAF magic and header offset class constants
  ([`32edf21`](https://github.com/djachenko/justin_utils/commit/32edf2113f37308412d36e11aaf1d2b1941f4e68))

- Narrow ImageSource to Path | IO[bytes], drop private PIL import
  ([`ac12695`](https://github.com/djachenko/justin_utils/commit/ac12695b2c6d24d44be9d4f296e11dae980fd667))

- Pass path to containers instead of a shared file handle
  ([`5dbf072`](https://github.com/djachenko/justin_utils/commit/5dbf072c1919bdf7ba0a6b4fbdf7285dc1131eae))

### Testing

- Extract raf container builder to drop duplicated header assembly
  ([`623c954`](https://github.com/djachenko/justin_utils/commit/623c954d3187fa76358eff43ab4c55c61b3163f9))


## v0.3.0 (2026-07-29)

### Chores

- Ignore CLAUDE.local.md
  ([`c24bde6`](https://github.com/djachenko/justin_utils/commit/c24bde6b075f3094e703a006bde09d26dc2ed3d7))

### Documentation

- Remove stale status and backlog from CLAUDE.md
  ([`ce127dd`](https://github.com/djachenko/justin_utils/commit/ce127dd96b96c900182605d1ba01e33d8bcbad40))

- Reorder modules section alphabetically, promote CLI tools
  ([`de7f0fc`](https://github.com/djachenko/justin_utils/commit/de7f0fcd68bf7968caed2d21c5c03d6a04b62e64))

### Features

- Add dictable module
  ([`ae0ee7c`](https://github.com/djachenko/justin_utils/commit/ae0ee7c0ef960e819d92f5722afc7ab7de1ea00c))

### Refactoring

- Remove frozendict dependency from dictable
  ([`7d8fb50`](https://github.com/djachenko/justin_utils/commit/7d8fb50bbc40892a2e707918f37806af0f2821f5))


## v0.2.3 (2026-07-29)

### Bug Fixes

- Add return type annotations for mypy --strict compliance
  ([`88af0ca`](https://github.com/djachenko/justin_utils/commit/88af0ca2b38363ca06e65797d5ae90926b7cbe66))

- Resolve ruff 0.16 violations (RUF012/013, C41x, UP028, B008, BLE001, PLR1722, DTZ, noqa)
  ([`0f2d878`](https://github.com/djachenko/justin_utils/commit/0f2d878cc08ea1fcf88d8d30aa56d75d54f02d46))

### Chores

- Pin ruff to >= 0.16, < 0.17
  ([`04157f0`](https://github.com/djachenko/justin_utils/commit/04157f0ea62cc2d790c319a041c4efe343540014))

### Code Style

- Apply ruff 0.16 auto-fixes (UP006/UP035, I001, C41x, B009)
  ([`91bf2d1`](https://github.com/djachenko/justin_utils/commit/91bf2d1af497b1b251a176cc339fc1bb3bcb6e4a))


## v0.2.2 (2026-06-30)

### Bug Fixes

- Allow None for metadata in ExternalMetadataSource type hint
  ([`eac8d77`](https://github.com/djachenko/justin_utils/commit/eac8d77efc69eefe7ebede1df76ebfb1aaca7b52))

### Chores

- Mark cli.py public classes as deprecated
  ([`00d95a7`](https://github.com/djachenko/justin_utils/commit/00d95a70ff0e3c0c9d97e11784992b63de8cbb49))


## v0.2.1 (2026-06-30)

### Bug Fixes

- DataSize.Unit.for_value off-by-one at exact unit boundaries
  ([`051f730`](https://github.com/djachenko/justin_utils/commit/051f730e969643beb539e7c9f87497794658a629))

- Remove now-empty source folder after renumber single-part flatten
  ([`04ffb38`](https://github.com/djachenko/justin_utils/commit/04ffb38514a55b1db8bf1ec1f71c93abc601d8b0))

### Code Style

- Add type hints to _run() in test_subfolder.py
  ([`9710541`](https://github.com/djachenko/justin_utils/commit/97105418b511bfce410e14f31db77e39c4cfd3b2))

- Blank line after first statement in _RecordingAction.__init__
  ([`27a4a5d`](https://github.com/djachenko/justin_utils/commit/27a4a5d645e522d2dba5f75200faf7d79b31cd6e))

- Type the recursive file-tree structure instead of bare dict
  ([`54f2d83`](https://github.com/djachenko/justin_utils/commit/54f2d83b0d9d9f5785c5d957d53b645b1ed2035f))

- Unify exception-test naming to _raises suffix
  ([`39f0553`](https://github.com/djachenko/justin_utils/commit/39f055376574c436135e531dde26127a85a5a275))

- Use collections.abc.Iterable and lowercase list[] in test_cli.py
  ([`1a83dbe`](https://github.com/djachenko/justin_utils/commit/1a83dbed078ee8ead8d93735cfb7cb5fc4bea0e1))

### Testing

- Add coverage for subfolder.py, fix mypy typing in test_cli.py
  ([`0c59307`](https://github.com/djachenko/justin_utils/commit/0c5930766742d08bccf3f7332f7a309ad1af7f56))

- Assert correct behavior for unit boundaries and renumber cleanup (red)
  ([`a6d4d14`](https://github.com/djachenko/justin_utils/commit/a6d4d14c95f9119023a67da0ac44ab957d3b8cfa))

- Cover case-insensitive extension matching in parse_sources
  ([`2ec5538`](https://github.com/djachenko/justin_utils/commit/2ec55380dd862f8e10f07bc3f9076568fd2f47d5))

- Deduplicate repeated string literals into single source of truth
  ([`2de5092`](https://github.com/djachenko/justin_utils/commit/2de5092688b1343ef1131061b1dfea84617a6921))

- Fix DataSpeed.formatted boundary test missed in previous audit
  ([`271cbd1`](https://github.com/djachenko/justin_utils/commit/271cbd1b8517e3b938903d00d2aaa2cdb0bdc11e))

- Fold case-insensitivity into existing parse_sources parametrize instead of new tests
  ([`d2d5eef`](https://github.com/djachenko/justin_utils/commit/d2d5eef388b36cb5aaabf0e877d5253f5cbfacf2))

- Fold duplicate-shaped tests into parametrize across the suite
  ([`fb7fcf6`](https://github.com/djachenko/justin_utils/commit/fb7fcf6f3405e9184655909d3d1e52d6bb528bed))

- Refactor test_parts.py to class+parametrize style
  ([`a94bde9`](https://github.com/djachenko/justin_utils/commit/a94bde9543ffcd34ad916a3043e646939ac5cd17))

- Use cross-product parametrize for extension-case combinations
  ([`bf6139d`](https://github.com/djachenko/justin_utils/commit/bf6139d5680712d61eac1b3042e47c46a53b892e))


## v0.2.0 (2026-06-30)

### Bug Fixes

- Clean up leftover temp folder in dump_in_temp
  ([`4565292`](https://github.com/djachenko/justin_utils/commit/4565292cebbe4a227d464031fabeb22b6b8bd5cc))

### Features

- Migrate parts CLI from argparse to Typer
  ([`2a5cf62`](https://github.com/djachenko/justin_utils/commit/2a5cf626f902f38274f077fa8048ba54210cb8b5))

### Testing

- Add tests for parts.py Typer CLI
  ([`cf850f8`](https://github.com/djachenko/justin_utils/commit/cf850f8be5c41bca85ec564423df89d0405b8e9c))


## v0.1.2 (2026-06-30)

### Bug Fixes

- Add path setter on FolderBased and drop unused pytest imports
  ([`983609c`](https://github.com/djachenko/justin_utils/commit/983609cda8deff699e9300003f41359835a26ac2))

- Folder.merge_into path update and __get_by_path single-component lookup
  ([`8ea2d62`](https://github.com/djachenko/justin_utils/commit/8ea2d62127c728e945071d657b9a5ceea68d09a5))

- Support Linux in __get_mount
  ([`e9ad807`](https://github.com/djachenko/justin_utils/commit/e9ad807f3b6b2a09742b32c3bf4a819bbcc7e2e3))

### Chores

- Add _worktrees/ to gitignore
  ([`8abfe6e`](https://github.com/djachenko/justin_utils/commit/8abfe6eeed64e90c16c7df042a51a46f8d45a5a5))

- Mark FolderBased as deprecated
  ([`6ddb233`](https://github.com/djachenko/justin_utils/commit/6ddb2332e9564eb7dd7a1aadf6aafc727138c871))

### Testing

- Add pytest suite for backlog bugs
  ([`3255843`](https://github.com/djachenko/justin_utils/commit/325584380b18522e9c02b4bd72a9620f2781d2eb))


## v0.1.1 (2026-06-27)

### Bug Fixes

- Add assertions for mypy in TransferSpeedMeter
  ([`9abdfe2`](https://github.com/djachenko/justin_utils/commit/9abdfe22253af2e2ee4ae0d30cfd8db0d414c0f5))

- Copy() no longer removes source tree on cross-drive copy
  ([`92e2d89`](https://github.com/djachenko/justin_utils/commit/92e2d893814a4c7d3c2ab7605330a034322e8620))

- Correct null checks in joins
  ([`d7ab2f5`](https://github.com/djachenko/justin_utils/commit/d7ab2f52fb64f7f1462940003b8f45d31f7be74d))

- Correct parse_date year logic for 4-digit years
  ([`cf7e703`](https://github.com/djachenko/justin_utils/commit/cf7e703c376cd7233c0f729961cde2cc50d07086))

- Make Exif.from_path abstract, Action inherit ABC
  ([`34d8cdc`](https://github.com/djachenko/justin_utils/commit/34d8cdcf2b4ca665474f27d69fc887d832e3cfec))

- Replace @property @cache with @cached_property
  ([`b07b020`](https://github.com/djachenko/justin_utils/commit/b07b020a4e49033a7f314a3b4b9acb1038a3bcb9))

### Chores

- [repokit] update ci workflows
  ([`0f1b1e5`](https://github.com/djachenko/justin_utils/commit/0f1b1e5ffde4b03d140b724d5b5eae327a2208f2))

- Bump minimum Python to 3.11, drop typing_extensions
  ([`284ff9c`](https://github.com/djachenko/justin_utils/commit/284ff9c0a682d835df67d64ba4c38283ea015fa9))

### Documentation

- Rewrite README
  ([`d898e99`](https://github.com/djachenko/justin_utils/commit/d898e999d1f9b5dab6015e3c24fa907903e09df7))

### Refactoring

- Expand ternary operators
  ([`37dede3`](https://github.com/djachenko/justin_utils/commit/37dede3c36407b2602971198255eda117b5236c3))


## v0.1.0 (2026-06-25)

- Initial Release
