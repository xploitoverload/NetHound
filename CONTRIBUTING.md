# Contributing to NetHound

Thanks for your interest in improving NetHound. Contributions of code, documentation, bug reports, and practical feedback are welcome.

## Before opening an issue

- Check whether a similar issue or feature request already exists.
- Include the NetHound version, Python version, operating system, command used, and a clear description of the problem.
- For collection issues, include the TLD and requested date.
- Share a small, sanitized example when possible. Do not include credentials, API tokens, private data, or sensitive logs.

## Local setup

```bash
git clone https://github.com/xploitoverload/NetHound.git
cd NetHound
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Verify the CLI is available:

```bash
nethound --version
nethound --help
nethound fetch --help
nethound search --help
nethound stats --help
```

For a basic Python syntax check:

```bash
python -m compileall nethound
```

## Pull request guidelines

1. Create a focused branch for your change.
2. Explain the problem and the behaviour your change introduces.
3. Keep changes scoped and update documentation when CLI behaviour changes.
4. Include reproduction steps or sample output where useful.
5. Do not commit downloaded domain archives, secrets, credentials, or unrelated generated files unless the change specifically requires them.
6. Open a pull request describing what changed and how you checked it.

## Data-source changes

When changing a data source or parser, document the source, expected input format, date handling, and failure behaviour. Avoid claiming complete TLD coverage unless it has been verified.

## Responsible use

NetHound supports domain discovery and security research. Contributions should not add functionality intended for unauthorized access, disruption, credential theft, or abuse.
