# QFIN List Page Version Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add auditable component versions, safe single-Skill rollback, historical Plugin installation, and release preparation without altering the existing platform Skill contents.

**Architecture:** Keep Git tags as immutable release snapshots, `versions.json` as the current machine-readable component lock, and `CHANGELOG.md` as the human release history. Three stdlib-only Python CLIs share validation and command-running code from `scripts/versioning_lib.py`; every mutating command is dry-run by default and requires `--apply`.

**Tech Stack:** Python 3.10 standard library, `unittest`, Git CLI, Codex Plugin CLI, existing Skill/Plugin validators.

**Spec:** `docs/superpowers/specs/2026-10-14-qfin-list-page-version-management-design.md`

## Global Constraints

- Do not modify business content under the four existing Skill directories while adding version management.
- Plugin version starts at `0.1.0`; router `0.1.0`; Yushu `1.3.2`; Jinyumeng `0.7.2`; Dianxiao `0.1.0`.
- Runtime code uses only the Python 3.10 standard library.
- All public CLIs default to dry-run; only `--apply` may write repository files or Plugin installation state.
- Never use `git reset --hard`, overwrite an existing tag, edit Plugin cache contents, or push to GitHub.
- A released rollback restores old behavior under a new monotonically increasing version.
- Git tags are the only formal rollback source; cache and manual archives are evidence or emergency recovery only.
- Tests that exercise Codex or Git mutations must use temporary repositories and fake command runners, never the real installed Plugin.

## Review Focus

- Dirty worktree containing both the declared component and unrelated files must fail before any version write; Task 2 tests this mixed-status case.
- Missing, malformed, or path-like tag values must fail closed before a worktree or restore command; Tasks 3 and 4 test invalid tags.
- A target tag missing `versions.json`, the selected Skill, or its `VERSION` must fail without changing the current tree; Tasks 3 and 4 test all three cases.
- A Codex CLI failure after the current Plugin is removed must restore the original marketplace and Plugin; Task 4 tests each failure boundary with a fake runner.
- Versions must not decrease or reuse an existing release number, including `0.x` versions; Tasks 1 and 2 test semantic ordering and existing-tag rejection.

---

### Task 1: Add the version lock, changelog baseline, and shared validation library

**Files:**
- Create: `versions.json`
- Create: `CHANGELOG.md`
- Create: `scripts/versioning_lib.py`
- Create: `tests/test_version_manifest.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: Plugin manifest and each Skill's `VERSION` file.
- Produces: `SemVer`, `VersionState`, `COMPONENTS`, `load_version_state(repo_root: Path) -> VersionState`, `validate_version_state(repo_root: Path) -> list[str]`, `read_versions_json(repo_root: Path) -> dict[str, object]`, `snapshot_component_trees(repo_root: Path, excluded: set[str]) -> dict[str, dict[str, FileRecord]]`, and `run_command(args: list[str], cwd: Path) -> CommandResult`.

- [ ] **Step 1: Write failing semantic-version and manifest tests**

Add tests asserting:

- `SemVer.parse("0.1.0") < SemVer.parse("0.1.1") < SemVer.parse("0.2.0") < SemVer.parse("1.0.0")`;
- malformed versions such as `1`, `v1.0.0`, `01.0.0`, and `1.0` raise `ValueError`;
- the published repository state matches the Plugin manifest and all four `VERSION` files;
- missing, extra, mismatched, or malformed components produce deterministic validation errors;
- `snapshot_component_trees(..., excluded={"yushu"})` returns manifests for exactly the other three component aliases plus `router` when the target is a platform, and never follows Plugin cache paths.

- [ ] **Step 2: Run the test and verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_version_manifest -v`

Expected: FAIL because `versions.json` and `scripts.versioning_lib` do not exist.

- [ ] **Step 3: Implement the shared data types and validation interfaces**

Use these exact public types:

```python
@dataclass(frozen=True, order=True)
class SemVer:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> "SemVer": ...
    def bump(self, level: str) -> "SemVer": ...
    def __str__(self) -> str: ...

@dataclass(frozen=True)
class VersionState:
    plugin: SemVer
    components: dict[str, SemVer]

@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
```

Pin `COMPONENTS` to aliases `router`, `yushu`, `jinyumeng`, and `dianxiao`, with exact directory names from the spec. Reuse `FileRecord` and `build_manifest` from `scripts.compare_skill_trees` for content-and-mode snapshots.

- [ ] **Step 4: Add the initial lock and changelog**

Create `versions.json` with `schemaVersion: 1`, Plugin `0.1.0`, router `0.1.0`, Yushu `1.3.2`, Jinyumeng `0.7.2`, and Dianxiao `0.1.0`. Create `CHANGELOG.md` with an initial `0.1.0` entry dated `2026-10-14`, listing all four component versions and tag `v0.1.0` as the baseline to be created after implementation.

Add `.qfin-backups/` and `.release-worktrees/` to `.gitignore`.

- [ ] **Step 5: Run Task 1 tests and repository tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_version_manifest -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS, and the existing root tests remain green.

- [ ] **Step 6: Commit Task 1**

```bash
git add .gitignore versions.json CHANGELOG.md scripts/versioning_lib.py tests/test_version_manifest.py
git commit -m "feat: add qfin release version manifest"
```

---

### Task 2: Implement dry-run-first release preparation

**Files:**
- Create: `scripts/release.py`
- Create: `tests/test_release.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 1 `SemVer`, `VersionState`, component mapping, manifest validation, and command runner.
- Produces: `ReleasePlan`, `detect_changed_components(repo_root: Path) -> tuple[set[str], list[str]]`, `plan_release(repo_root: Path, components: tuple[str, ...], bump: str, note: str, plugin_bump: str | None = None) -> ReleasePlan`, and `apply_release(repo_root: Path, plan: ReleasePlan) -> None`.

- [ ] **Step 1: Write failing release planning tests**

Use temporary Git repositories copied from a minimal fixture. Assert:

- a Yushu-only edit plans `1.3.2 -> 1.3.3` and Plugin `0.1.0 -> 0.1.1` while other component versions remain unchanged;
- `--component router` maps to `qfin-list-page` and never to a platform child;
- multiple `--component` flags update only the named components;
- a clean tree, unrelated dirty path, undeclared changed component, invalid bump, Plugin bump lower than component bump, and an already-existing target tag all fail closed;
- dry-run leaves every file byte-identical and creates no commit or tag;
- apply updates only selected `VERSION` files, Plugin manifest, `versions.json`, and `CHANGELOG.md`;
- apply does not commit or create a tag;
- versions never decrease or reuse a previously tagged Plugin version.

- [ ] **Step 2: Run tests and verify they fail**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_release -v`

Expected: FAIL because `scripts.release` does not exist.

- [ ] **Step 3: Implement release planning and apply interfaces**

Use this exact public model:

```python
@dataclass(frozen=True)
class ReleasePlan:
    current: VersionState
    target: VersionState
    components: tuple[str, ...]
    bump: str
    plugin_bump: str
    note: str
    tag: str
    changed_paths: tuple[str, ...]
```

`detect_changed_components` reads `git status --porcelain=v1 --untracked-files=all`. It permits changes only under declared component roots before apply; it treats all other paths as blocking unrelated changes. `plan_release` verifies component aliases, actual changes, semantic ordering, target-tag absence, and Plugin bump severity.

`apply_release` updates the selected component `VERSION` files, Plugin manifest JSON, `versions.json`, and prepends one deterministic release section to `CHANGELOG.md`. It then runs manifest validation and returns without committing or tagging.

- [ ] **Step 4: Implement the CLI**

CLI contract:

```text
release.py --component ALIAS [--component ALIAS ...]
           --bump patch|minor|major
           --note TEXT
           [--plugin-bump patch|minor|major]
           [--apply]
```

Without `--apply`, print the current and target version matrix, changed paths, changelog preview, validation commands, and proposed tag. With `--apply`, print the same plan, apply it, run the target component tests plus root/router/Plugin validation, and stop nonzero on failure.

- [ ] **Step 5: Run tests and a real dry-run fixture check**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_release -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS. Do not run `--apply` against the real repository because version-management tooling alone does not change Plugin-distributed behavior.

- [ ] **Step 6: Document release usage and commit**

Add README examples for dry-run, `--apply`, manual review, commit, and annotated tag creation. State that pushing remains manual.

```bash
git add scripts/release.py tests/test_release.py README.md
git commit -m "feat: add dry run qfin release workflow"
```

---

### Task 3: Implement isolated single-Skill rollback

**Files:**
- Create: `scripts/rollback_skill.py`
- Create: `tests/test_rollback_skill.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 1 component mapping and tree snapshots; Task 2 release command contract.
- Produces: `RollbackPlan`, `plan_skill_rollback(repo_root: Path, skill: str, tag: str) -> RollbackPlan`, and `apply_skill_rollback(repo_root: Path, plan: RollbackPlan, now: datetime | None = None) -> Path` returning the backup directory.

- [ ] **Step 1: Write failing rollback tests in temporary Git repositories**

Create a fixture with a baseline tag, then modify one component and commit the new state. Assert:

- `router`, `yushu`, `jinyumeng`, and `dianxiao` map to the exact expected directories;
- dry-run reports file additions, removals, content changes, mode changes, current version, historical version, and preserved current `VERSION`;
- dry-run creates no backup and changes no file;
- apply creates `.qfin-backups/<timestamp>/<skill-directory>/` and restores only target behavior files;
- apply preserves the current target `VERSION` rather than copying the historical version;
- every non-target component manifest remains identical;
- invalid component, malformed tag, missing tag, missing target Skill, missing historical `VERSION`, dirty tree, and a target tag with path traversal syntax fail before mutation;
- simulated post-restore invariant failure restores the target from backup;
- the printed next command uses `release.py --component <alias> --bump patch`.

- [ ] **Step 2: Run tests and verify they fail**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_rollback_skill -v`

Expected: FAIL because `scripts.rollback_skill` does not exist.

- [ ] **Step 3: Implement rollback planning and application**

Use this exact public model:

```python
@dataclass(frozen=True)
class RollbackPlan:
    skill: str
    tag: str
    target_path: str
    current_version: SemVer
    historical_version: SemVer
    differences: tuple[str, ...]
    non_target_manifests: dict[str, dict[str, FileRecord]]
```

Validate tags with `git check-ref-format --allow-onelevel` and additionally require the `v<semver>` form. Read historical files with `git ls-tree`/`git show` during planning. Application copies the current target to backup, restores only that Git path, rewrites the saved current `VERSION`, verifies non-target manifests, and restores the backup on any failure.

- [ ] **Step 4: Implement the CLI**

CLI contract:

```text
rollback_skill.py --skill router|yushu|jinyumeng|dianxiao
                  --to v<semver>
                  [--apply]
```

Dry-run prints the plan and exact next steps. Apply runs the target Skill tests and its validator, then prints the required `release.py` command; it never changes Plugin or Skill version numbers itself.

- [ ] **Step 5: Run rollback and full repository tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_rollback_skill -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS.

- [ ] **Step 6: Document and commit Task 3**

```bash
git add scripts/rollback_skill.py tests/test_rollback_skill.py README.md
git commit -m "feat: add isolated skill rollback workflow"
```

---

### Task 4: Implement historical Plugin installation with automatic recovery

**Files:**
- Create: `scripts/install_version.py`
- Create: `tests/test_install_version.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 1 manifest validation and command-result abstraction.
- Produces: `InstallPlan`, `plan_install(repo_root: Path, tag: str, runner: Runner) -> InstallPlan`, `apply_install(repo_root: Path, plan: InstallPlan, runner: Runner) -> None`, and `restore_current(repo_root: Path, runner: Runner) -> None`. `Runner` is any callable `(args: list[str], cwd: Path) -> CommandResult`.

- [ ] **Step 1: Write failing install planner tests with a fake runner**

Assert:

- a valid `v<semver>` tag plans a detached worktree under `.release-worktrees/<tag>` and reports all component versions;
- dry-run makes no Git worktree, marketplace, Plugin, or file changes;
- malformed/missing tags, missing historical `versions.json`, mismatched historical manifest, or absent Plugin files fail before Codex mutation;
- apply command order is worktree validation, current Plugin remove, marketplace remove, historical marketplace add, Plugin add, and installed-state verification;
- failure after each mutating Codex command invokes restoration of the original repository marketplace and Plugin;
- `--restore-current` removes the historical install, re-adds the main repository marketplace, installs `qfin-list-page@qfin-list-page`, and verifies enabled state;
- existing unrelated worktrees are never removed;
- paths derived from tags remain under `.release-worktrees/`.

- [ ] **Step 2: Run tests and verify they fail**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_version -v`

Expected: FAIL because `scripts.install_version` does not exist.

- [ ] **Step 3: Implement planning, command execution, and recovery**

Use this exact public model:

```python
@dataclass(frozen=True)
class InstallPlan:
    tag: str
    worktree_path: Path
    historical_state: VersionState
    original_marketplace_path: Path
    original_plugin_version: SemVer
```

Planning uses read-only Git commands and reads `versions.json` plus Plugin/Skill versions from the tagged tree. Application creates only its own detached worktree, validates it, then executes Codex commands. Wrap all Codex mutations in recovery that re-registers `original_marketplace_path` and reinstalls the original Plugin.

- [ ] **Step 4: Implement the CLI**

CLI contract:

```text
install_version.py --tag v<semver> [--apply]
install_version.py --restore-current [--apply]
```

Print the component matrix, current install, command plan, recovery plan, and the requirement to open a new Codex task. Do not delete historical worktrees automatically; print the safe cleanup command after the user restores current.

- [ ] **Step 5: Run install-version and full repository tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_version -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS. Do not run `--apply` against the user's live Plugin during implementation; Task 5 verifies only dry-run against the real repository.

- [ ] **Step 6: Document and commit Task 4**

```bash
git add scripts/install_version.py tests/test_install_version.py README.md
git commit -m "feat: add historical qfin plugin installer"
```

---

### Task 5: Integrate, validate, and establish the immutable v0.1.0 baseline

**Files:**
- Modify: `tests/test_plugin_layout.py`
- Modify: `README.md`
- Modify: `docs/import-integrity-2026-10-13.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: all Task 1-4 public CLIs and validation interfaces.
- Produces: one documented, fully validated release workflow and local annotated Git tag `v0.1.0`.

- [ ] **Step 1: Add failing integration assertions**

Extend layout tests to require `versions.json`, `CHANGELOG.md`, all three public CLIs, README examples for release/single-Skill rollback/full-Plugin rollback, and explicit statements that commands dry-run by default and never edit Plugin cache.

- [ ] **Step 2: Run integration tests and verify any missing documentation fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: FAIL only for any still-missing integration documentation or layout contract.

- [ ] **Step 3: Complete README and integrity evidence**

Document the normal release flow, single-Skill recovery, temporary Plugin downgrade, restoration to current, manual commit/tag step, and new-task runtime pickup. Record that version-management introduction did not change any of the four Skill trees.

- [ ] **Step 4: Run all repository and Skill validation**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/qfin-list-page/skills/qfin-list-page/tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 plugins/qfin-list-page/skills/qfin-list-page/scripts/validate_router.py
UV_CACHE_DIR=/private/tmp/qfin-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --with pyyaml python /Users/panyue/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/qfin-list-page/skills/qfin-list-page
UV_CACHE_DIR=/private/tmp/qfin-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --with pyyaml python /Users/panyue/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/qfin-list-page
```

Run every child test suite and contract validator as documented in `docs/import-integrity-2026-10-13.md`.

Expected: every command PASS.

- [ ] **Step 5: Prove the four Skill trees were not changed**

Run:

```bash
git diff 26051cf -- plugins/qfin-list-page/skills/qfin-list-page plugins/qfin-list-page/skills/qifu-yushu-list-page plugins/qfin-list-page/skills/qifu-jinyumeng-list-page plugins/qfin-list-page/skills/qifu-dianxiao-list-page
```

Expected: no output. Also run `python3 scripts/install_version.py --tag v0.1.0` only after the tag is created; expected dry-run output with no Plugin state changes.

- [ ] **Step 6: Commit the integration evidence**

```bash
git add README.md tests/test_plugin_layout.py docs/import-integrity-2026-10-13.md CHANGELOG.md
git commit -m "docs: complete qfin version recovery workflow"
```

- [ ] **Step 7: Create the local baseline tag and verify it**

Preconditions: `git status --short` is empty, no `v0.1.0` tag exists, and all validation passed against HEAD.

Run:

```bash
git tag -a v0.1.0 -m "qfin-list-page plugin v0.1.0"
git show --no-patch --decorate v0.1.0
python3 scripts/install_version.py --tag v0.1.0
```

Expected: annotated tag points to the final validated commit; installer dry-run reports Plugin `0.1.0` and the four pinned component versions without changing the live install. Do not push the tag.

## Final Verification Gate

Before claiming completion:

1. `git status --short` is empty.
2. `git log --oneline` contains one commit per task plus the approved spec and plan commits.
3. `git tag --list v0.1.0` returns exactly `v0.1.0`.
4. Every root, router, and child test suite passes.
5. Router, Skill, child-contract, and Plugin validators pass.
6. `validate_version_state` returns no errors.
7. All three public CLIs show dry-run output without mutating real files or installed Plugin state.
8. The four Skill trees have no diff from commit `26051cf`.
9. The current live Plugin remains installed and enabled at `0.1.0`.
10. No GitHub push or Figma mutation occurred.
