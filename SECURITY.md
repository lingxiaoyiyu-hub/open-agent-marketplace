# Security Policy

## Security & Privacy Commitment

The **Antigravity Plugin Marketplace** adheres to strict security and desensitization guidelines:

- **No Secrets in Source**: All plugins published in this marketplace are sanitized to ensure zero hardcoded tokens, secret keys, or credentials.
- **Environment Variable Scoping**: External services (such as StepFun API, OpenAI API, Frida endpoints) obtain credentials exclusively via local environment variables set by the user.

## Reporting Vulnerabilities

If you discover a security vulnerability or sensitive key leak within any plugin in this repository:

1. **Do NOT open a public issue.**
2. Report the vulnerability directly to the repository maintainer via GitHub Private Vulnerability Reporting or via email to `lingxiaoyiyu-hub@users.noreply.github.com`.
3. The issue will be acknowledged within 24 hours and patched promptly.
