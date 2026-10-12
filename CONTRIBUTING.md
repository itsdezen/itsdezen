# Git conventions

## Human-authored commits

- Prefix commit subjects with an emoji that communicates the change, followed
  by a concise English summary. Examples from this repository include
  `🚀 add self-updating README`, `🐞 fix links rendering`, and
  `🔧 update build workflow`.
- Common prefixes: `🚀` feature, `🐞` fix, `🔧` maintenance, `📝` docs, and
  `🎨` visual/design changes. Keep commits focused and omit a trailing period.

## Automated README updates

The GitHub Actions workflow may create `Update README.md` commits when its
generated README content changes. Leave that workflow-generated subject as-is;
do not use it for manually authored commits.

## Branches

- Name topic branches with up to three lowercase, hyphen-separated words;
  do not use slash-separated type prefixes (for example, `readme-workflow`).
- Keep `main` as the stable branch. Push a topic branch to its matching
  origin branch after its checks pass.
