# Contributing to Open Agent Marketplace

Thank you for considering contributing to **Open Agent Marketplace**! We welcome custom skills, rules, hooks, and MCP servers from the community.

## 🛠️ How to Add a New Plugin

1. **Fork the Repository**: Create your own fork of `lingxiaoyiyu-hub/open-agent-marketplace`.
2. **Create a Plugin Directory**: Add your plugin folder under `./plugins/<your-plugin-name>/`.
3. **Define `plugin.json`**: Ensure your plugin directory contains a valid `plugin.json` manifest.
4. **Update `marketplace.json`**: Register your plugin entry in the root `marketplace.json` file.
5. **Sanitize Secrets**: Ensure no hardcoded API keys, private tokens, or personal local paths are included.
6. **Submit a Pull Request**: Submit a PR targeting the `main` branch with a clear summary of your plugin's capabilities.

## 📐 Plugin Structure Standard

```text
plugins/<plugin_name>/
├── plugin.json       # Required: Plugin manifest
├── mcp_config.json   # Optional: MCP servers exposed by the plugin
├── hooks.json        # Optional: Lifecycle hooks
├── README.md         # Recommended: Documentation
├── rules/            # Optional: Markdown rules (*.md)
└── skills/           # Optional: Agent skills
    └── <skill_name>/
        └── SKILL.md
```

## 🔒 Security Guidelines

- Never commit real API keys or tokens. Use environment variable placeholders (`os.getenv("API_KEY")` or `${ENV_VAR}`).
- Ensure binary tools or scripts included pass static security checks.
