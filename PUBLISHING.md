# Publishing Guide for ARES MCP Server

## One-Time Setup

### 1. Create PyPI Account
1. Register at https://pypi.org/account/register/
2. Enable 2-Factor Authentication (required)
3. Go to https://pypi.org/manage/account/token/
4. Create an API token with scope "Entire account"
5. Save the token securely (starts with `pypi-`)

### 2. Configure GitHub Repository for Trusted Publishing
1. Go to your PyPI account settings
2. Navigate to "Publishing" → "Add a new pending publisher"
3. Fill in:
   - PyPI Project Name: `ares-mcp-server`
   - Owner: `vzeman`
   - Repository name: `ares-mcp-server`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
4. Click "Add"

### 3. (Optional) Set up TestPyPI
Repeat the above for https://test.pypi.org/ with environment name `testpypi`

## Publishing Process

### Method 1: Automated via GitHub Release (Recommended)

1. Update version number in:
   - `pyproject.toml`
   - `ares_mcp_server/__init__.py`

2. Update `CHANGELOG.md` with release notes

3. Commit and push:
   ```bash
   git add -A
   git commit -m "Release v0.3.3"
   git push origin main
   ```

4. Create a GitHub release:
   ```bash
   git tag v0.3.3
   git push origin v0.3.3
   ```
   Or use GitHub UI: Go to Releases → "Create a new release"

5. The GitHub Action will automatically:
   - Build the package
   - Run tests
   - Publish to PyPI

### Method 2: Manual Publishing

1. Build the package:
   ```bash
   pyproject-build
   ```

2. Check the build:
   ```bash
   twine check dist/*
   ```

3. Upload to TestPyPI (optional):
   ```bash
   twine upload --repository testpypi dist/*
   ```

4. Test installation from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ ares-mcp-server
   ```

5. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```
   - Username: `__token__`
   - Password: Your PyPI API token

### Method 3: Manual Trigger via GitHub Actions

1. Go to Actions → "Publish to PyPI" workflow
2. Click "Run workflow"
3. Choose branch and whether to publish to TestPyPI
4. Click "Run workflow"

## Post-Publishing

1. Verify installation:
   ```bash
   pip install ares-mcp-server
   ares-mcp-server --version
   ```

2. Test the package:
   ```bash
   python -c "from ares_mcp_server import __version__; print(__version__)"
   ```

3. Update documentation if needed

## Version Management

- Use semantic versioning: MAJOR.MINOR.PATCH
- Update version in both `pyproject.toml` and `__init__.py`
- Tag releases with `v` prefix: `v0.3.3`

## Troubleshooting

### Authentication Issues
- Ensure your PyPI token starts with `pypi-`
- Use `__token__` as username, not your PyPI username
- Check token permissions (should be "Entire account" or project-specific)

### Build Issues
- Clean build artifacts: `rm -rf dist/ build/ *.egg-info`
- Ensure all files are committed to git
- Check `MANIFEST.in` includes all necessary files

### GitHub Actions Issues
- Check workflow logs in Actions tab
- Ensure trusted publishing is configured in PyPI
- Verify environment names match (`pypi` and `testpypi`)

## Security Notes

- Never commit PyPI tokens to the repository
- Use GitHub's trusted publishing (no tokens needed)
- Keep your PyPI account secure with 2FA
- Regularly review and rotate API tokens