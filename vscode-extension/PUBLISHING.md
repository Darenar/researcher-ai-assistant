# Publishing to the Visual Studio Marketplace

The extension source, bundle configuration, icon, Marketplace metadata,
license, changelog, and GitHub publishing workflow are already included.

## One-time account setup

1. Create an Azure DevOps organization if you do not already have one.
2. Create a Visual Studio Marketplace publisher at
   <https://marketplace.visualstudio.com/manage/publishers/>.
3. Use `darenar` as the publisher ID. If that ID is unavailable, change the
   `publisher` field in `package.json` to the ID you create.
4. Create an Azure DevOps Personal Access Token with Marketplace management
   permission.
5. Never add the token to this repository.

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

## Publish locally

```bash
npx vsce login darenar
npm run publish:marketplace
```

If you used another publisher ID, substitute it in the login command and in
`package.json`.

## Publish with GitHub Actions

1. Add the Personal Access Token as a repository secret named `VSCE_PAT`.
2. Update `version` in `package.json` and add the release notes to
   `CHANGELOG.md`.
3. Commit and push the change.
4. Create and push a matching tag, for example:

   ```bash
   git tag extension-v0.1.0
   git push origin extension-v0.1.0
   ```

The `Publish VS Code extension` workflow validates, bundles, and publishes the
release. It can also be started manually from the GitHub Actions page.

After the first release is accepted, users can search for **Research AI
Assistant** in VS Code and click **Install**. Marketplace updates are delivered
through VS Code's normal extension update mechanism.
