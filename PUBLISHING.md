# Publishing to PyPI

This document explains how to publish the `kaizen-code` package to PyPI.

---

## Method 1: Automated Publishing via GitHub Actions (Recommended)

This project includes a GitHub Actions workflow (`.github/workflows/publish.yml`) that automatically builds and publishes the package to PyPI whenever you push a version tag (e.g., `v0.1.0`).

To use this, you must set up **Trusted Publishing (OIDC)** on PyPI:

1. **Log in to PyPI**: Go to [pypi.org](https://pypi.org/) and log in to your account.
2. **Add a Trusted Publisher**:
   - Go to **Account Settings** -> **Publishing** -> **Add a new publisher**.
   - Select **GitHub** as the provider.
   - Enter the following details:
     - **Owner**: `arunpunithkumar3-a11y`
     - **Repository**: `Kaizen-Code`
     - **Workflow Name**: `publish.yml`
     - **Environment Name**: `pypi`
3. **Trigger the Workflow**:
   - When you are ready to publish a new version, update the version number in `pyproject.toml` (e.g., `version = "0.1.0"`).
   - Create and push a git tag for that version:
     ```bash
     git tag v0.1.0
     git push origin v0.1.0
     ```
   - GitHub Actions will spin up, build the package, verify it, and upload it securely to PyPI.

---

## Method 2: Manual Publishing

If you prefer to publish manually from your local command line, follow these steps:

### 1. Install Build Tools
Make sure you have `build` and `twine` installed:
```bash
python -m pip install --upgrade build twine
```

### 2. Build the Package
From the root directory of the project, run:
```bash
python -m build
```
This generates build artifacts in the `dist/` directory:
- A source distribution (`.tar.gz`)
- A built distribution wheel (`.whl`)

### 3. Verify the Build
Verify that the build descriptions render correctly on PyPI:
```bash
python -m twine check dist/*
```

### 4. Upload to PyPI
Upload the distributions to PyPI using twine:
```bash
python -m twine upload dist/*
```
*Note: You will be prompted to enter your PyPI username (use `__token__`) and your API token password.*

---

## Testing Your Installation

Once published, you and other users can install Kaizen using:
```bash
pip install kaizen-code
```

To verify the installation:
```bash
# Check if CLI works
kaizen --help

# Check if library import works
python -c "import kaizen; print(kaizen.__file__)"
```
