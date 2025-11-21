### Testing
- Use pytest

## Dependencies
- Dependencies are managed via requirements.txt
- When adding new dependencies, add them to requirements.txt
- The project uses a Python virtual environment located at `.chess-theme-classifier/`
- Always activate the virtual environment before running any commands: `source .chess-theme-classifier/bin/activate`
- If new dependencies are needed, add them to requirements.txt and run then run `pip install -r requirements.txt`
- Required third-party packages include: PyTorch, torchvision, pandas, numpy, scikit-learn, matplotlib, etc. (see requirements.txt)
- Verify that installation succeeds before committing changes

## Security and Credentials
- NEVER store API keys, passwords, or other credentials in source code
- Use environment variables for sensitive information:
  - For Weights & Biases: Set WANDB_API_KEY or use `wandb login` command
  - Store credentials in .env files (add to .gitignore)
  - Document required environment variables in README.md
- When writing code that requires credentials, always use environment variables or config files
- For dev environments, add instructions for setting up credentials

## Style Guidelines
- Formatting: 4-space indentation
- Imports: stdlib → third-party → local modules
- Naming: snake_case for variables/functions, CamelCase for classes
- Documentation: Use docstrings for functions and classes
- Types: Add type hints for function parameters and return values
- Error handling: Use try/except blocks for expected exceptions