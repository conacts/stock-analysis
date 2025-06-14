# 🧹 Project Cleanup & Reorganization Plan

**Systematic cleanup and reorganization of the stock-analysis project**

## 📋 Current Status

-   **Phase 1**: Portfolio Management System ✅ COMPLETED
-   **Phase 2**: Testing Infrastructure & CI/CD ✅ COMPLETED
-   **Phase 3**: LLM-Enhanced Analysis ✅ COMPLETED
-   **Phase 4**: Project Cleanup & Reorganization 🔄 IN PROGRESS

## 🎯 Cleanup Objectives

1. **Remove unused and redundant files**
2. **Consolidate configuration files**
3. **Organize files by purpose and functionality**
4. **Improve code coverage to 70%+**
5. **Streamline development workflow**

## 🗑️ Files to Remove/Clean Up

### Unused Output Files

-   [ ] `output/llm_prompt_2025-06-13.txt` - Temporary LLM prompt file
-   [ ] `coverage.xml` - Can be regenerated, not needed in repo
-   [ ] `.coverage` - Can be regenerated, not needed in repo
-   [ ] `htmlcov/` directory - Can be regenerated, should be in .gitignore

### Configuration Consolidation

-   [ ] **setup.cfg** - Can be consolidated into pyproject.toml
    -   Contains only flake8 configuration
    -   Modern Python projects use pyproject.toml for all config
-   [ ] **pytest.ini** - Can be consolidated into pyproject.toml
    -   All pytest config can go in [tool.pytest.ini_options]

### Documentation Review

-   [ ] **Multiple README files** - Consolidate overlapping content
    -   Main `README.md` (keep as primary)
    -   `src/README.md` (merge relevant content, then remove)
-   [ ] **Archive directory cleanup**
    -   `archive/README.md` - Review if still needed
    -   `archive/IMPROVEMENT_ROADMAP.md` - Outdated, can be removed

### Empty/Unused Directories

-   [ ] `migrations/` - Empty directory, can be removed
-   [ ] `.obsidian/` - IDE-specific, should be in .gitignore only

## 📁 File Structure Analysis

### Current Root Directory (21 files + 11 directories)

```
✅ KEEP (Core files):
- Makefile (updated with new script paths)
- pyproject.toml (main configuration)
- .pre-commit-config.yaml (development workflow)
- .gitignore (version control)
- run_tests.py (test runner)
- README.md (main documentation)
- uv.lock (dependency lock file)
- .python-version (Python version specification)

📝 REVIEW/CONSOLIDATE:
- setup.cfg → merge into pyproject.toml
- pytest.ini → merge into pyproject.toml
- DEVELOPMENT.md (consolidate with README?)
- CONFIGURATION.md (consolidate with README?)
- GLOSSARY.md (move to docs/ or consolidate?)

🗑️ REMOVE:
- coverage.xml (generated file)
- .coverage (generated file)
- TODO.md (keep for now, but consider moving to docs/)
- CLEANUP_PLAN.md (temporary, remove after cleanup)

📂 DIRECTORIES:
✅ Keep: src/, tests/, scripts/, .git/, .github/, data/, docs/, .venv/
🗑️ Remove: migrations/ (empty), htmlcov/ (generated)
📝 Review: archive/, output/, .obsidian/
```

## 🗂️ Reorganization Tasks

### Phase 4.1: Remove Unused Files (IMMEDIATE)

-   [x] **Move standalone scripts to scripts/** ✅ COMPLETED

    -   [x] alert_manager.py → scripts/
    -   [x] portfolio_manager.py → scripts/
    -   [x] main_app.py → scripts/
    -   [x] master_stock_analyzer.py → scripts/
    -   [x] migrate.py → scripts/
    -   [x] Update import paths in moved files ✅ COMPLETED

-   [ ] **Remove generated/temporary files**

    -   [ ] Remove `coverage.xml`
    -   [ ] Remove `.coverage`
    -   [ ] Remove `htmlcov/` directory
    -   [ ] Remove `output/llm_prompt_2025-06-13.txt`
    -   [ ] Remove empty `migrations/` directory

-   [ ] **Clean up IDE-specific files**
    -   [ ] Remove `.obsidian/` directory (IDE-specific)
    -   [ ] Ensure it's properly ignored in .gitignore

### Phase 4.2: Configuration Consolidation

-   [ ] **Consolidate setup.cfg into pyproject.toml**

    -   [ ] Move flake8 configuration to [tool.flake8] section
    -   [ ] Remove setup.cfg file
    -   [ ] Test that linting still works

-   [ ] **Consolidate pytest.ini into pyproject.toml**
    -   [ ] Move pytest configuration to [tool.pytest.ini_options]
    -   [ ] Remove pytest.ini file
    -   [ ] Test that all pytest functionality works

### Phase 4.3: Documentation Consolidation

-   [ ] **Review and consolidate README files**

    -   [ ] Review `src/README.md` content
    -   [ ] Merge useful content into main README.md
    -   [ ] Remove `src/README.md`
    -   [ ] Update setup and usage instructions

-   [ ] **Archive cleanup**

    -   [ ] Review `archive/` contents
    -   [ ] Remove outdated `archive/IMPROVEMENT_ROADMAP.md`
    -   [ ] Keep `archive/README.md` if it has historical value

-   [ ] **Documentation organization**
    -   [ ] Consider moving DEVELOPMENT.md to docs/
    -   [ ] Consider moving CONFIGURATION.md to docs/
    -   [ ] Consider moving GLOSSARY.md to docs/

### Phase 4.4: Final Organization

-   [ ] **Update .gitignore**

    -   [ ] Ensure all generated files are ignored
    -   [ ] Add htmlcov/, .coverage, coverage.xml
    -   [ ] Add .obsidian/ if not already there

-   [ ] **Test everything works**
    -   [ ] Run full test suite
    -   [ ] Test all Makefile targets
    -   [ ] Test all scripts from new locations
    -   [ ] Verify CI/CD pipeline

## 🔧 Implementation Steps

### Step 1: Remove Unused Files (Today)

```bash
# Remove generated files
rm -f coverage.xml .coverage
rm -rf htmlcov/

# Remove temporary output files
rm -f output/llm_prompt_2025-06-13.txt

# Remove empty directories
rmdir migrations/ 2>/dev/null || true

# Remove IDE-specific directories
rm -rf .obsidian/
```

### Step 2: Configuration Consolidation (Today)

```bash
# Backup current configs
cp setup.cfg setup.cfg.bak
cp pytest.ini pytest.ini.bak

# After consolidating into pyproject.toml:
# rm setup.cfg pytest.ini
```

### Step 3: Documentation Review (This Week)

-   Consolidate README files
-   Clean up archive directory
-   Organize documentation in docs/

## 📊 Success Metrics

### File Cleanup

-   [ ] Root directory reduced from 21 files to ~15 files
-   [ ] All generated files removed from repo
-   [ ] Configuration consolidated into pyproject.toml
-   [ ] Documentation streamlined

### Code Quality

-   [ ] All tests passing after cleanup
-   [ ] Import paths working correctly
-   [ ] No broken references
-   [ ] CI/CD pipeline unaffected

### Development Workflow

-   [ ] All Makefile targets work
-   [ ] Scripts run from new locations
-   [ ] Configuration changes don't break tools
-   [ ] Documentation is clear and current

## 🚨 Risk Mitigation

### Before Making Changes

-   [x] Commit current state ✅ COMPLETED
-   [x] Run full test suite ✅ COMPLETED
-   [x] Document current working state ✅ COMPLETED

### During Changes

-   [ ] Make incremental changes
-   [ ] Test after each major change
-   [ ] Commit frequently with descriptive messages
-   [ ] Keep backups of important config files

### After Changes

-   [ ] Run full test suite
-   [ ] Test all scripts manually
-   [ ] Verify CI/CD pipeline
-   [ ] Update documentation

## 📝 Notes

-   Focus on removing truly unused files, not just cache directories
-   Configuration consolidation follows modern Python best practices
-   All changes should maintain backward compatibility where possible
-   Test thoroughly before committing each phase

---

**Next Action**: Start with Phase 4.1 - Remove Unused Files
