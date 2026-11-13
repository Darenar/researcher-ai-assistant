# Publishing to the Visual Studio Marketplace

The extension source, bundle configuration, icon, Marketplace metadata,
license, changelog, and GitHub publishing workflow are included.

## One-time Marketplace setup

The Marketplace publisher is:

```text
Publisher name: Vladislav Pyzhov
Publisher ID: VladislavPyzhov
```

Open <https://marketplace.visualstudio.com/manage/publishers/>, select the
`VladislavPyzhov` publisher, and create a **Trusted Publishing** policy with
these exact values:

```text
Policy name: Research Assistant releases
Repository owner: Darenar
Repository: researcher-ai-assistant
Workflow: publish-extension.yml
Environment: leave empty
```

This policy lets the GitHub Actions workflow obtain a short-lived publishing
credential through OpenID Connect. Do not create or store a Marketplace PAT.

## Validate a release locally

From `vscode-extension/`:

```bash
npm ci
npm run check
npm test
npm run package
```

This creates `research-ai-assistant-<version>.vsix`. Install it in a clean VS
Code profile and verify API-key setup, a question, dry-run formatting, and real
formatting before publishing.

## Publish with GitHub Actions

1. Update `version` in `package.json` and add the release notes to
   `CHANGELOG.md`.
2. Commit and push the change.
3. Create and push a matching tag, for example:

   ```bash
   git tag extension-v0.1.0
   git push origin extension-v0.1.0
   ```

The `Publish VS Code extension` workflow validates, bundles, and publishes the
release through the Trusted Publishing policy. No GitHub secret is required.
The workflow can also be started manually from the GitHub Actions page.

After the first release is accepted, users can search for **Research AI
Assistant** in VS Code and click **Install**. Marketplace updates are delivered
through VS Code's normal extension update mechanism.
