# Skill for model selection
Why? So subagents can better select models based on real data.

How? It uses Artificial Analysis' API (sorry, you need to sign up for an account, but it's free)
This caches the API calls on a daily basis (in `~/.cache/model-selection/`, or `$MODEL_SELECTION_CACHE_DIR`), so it
doesn't blow the 100 req/day free tier limit. You're good.

This fork (hughescr/model-selection) is packaged as a Claude Code plugin: the skill lives in `skills/model-selection/`
with its script and references, and `.claude-plugin/plugin.json` sits at the root. It also holds the facts behind the
agent routes in hughescr/claude-code-config; the Claude routes it names are that repo's `craig-core:*` plugin agents.

The original was one-shotted by tkellogg; the prompt below is kept as its origin story. The `creds.json` it mentions is
gone: see Credentials.

I one-shotted this in Codex with `gpt-5.6-luna/xhigh` using the following prompt:

> create a skill here, fill it out. I've saved creds.json with the credentials for a free account with artificial
> analysis, here's there docs: https://artificialanalysis.ai/api-reference

> Coerce the docs into markdown needed to operate this skill. I also want API calls cached here on disk, probably within
> the skill, or just temp files, idc

> The purpose of the skill is to select models for tasks based on costs & benchmark scores. The agent needs to first
> know what model options are available to it. e.g. if it's in Claude Code, there must be some way to figure out what
> models are available from within Claude Code. Same with Codex. Also, go lookup detail on each of the benchmarks and
> create one file for coding benchmarks, another for writing, etc. Break it down topic-wise and use the file to explain
> what each benchmark means, it's pros/cons, possible shortcomings, and what people think it indicates. Here, I'm
> expecting you to do real deep research on each benchmark in subagents. For the skill, maybe include a python snippets
> for formatting models various ways. I think it would be useful to see them ordered by perf on coding benchies, but
> then include all benchmarks to see how the writing is, etc. Cost is another big one, worth an example showing how to
> display cost per intelligence.

> k, i'm excited to see what you come up with

# Install
As a plugin, from the marketplace in hughescr/claude-code-config:

```
/plugin marketplace add hughescr/claude-code-config
/plugin install model-selection@craigs-claude-plugins
```

To try local, unpushed changes from a clone, load the clone directly for one session:

```bash
claude --plugin-dir ~/code/hughescr/model-selection
```

Do not clone it into `~/.claude/skills/`: a directory there with a plugin manifest auto-loads as
`model-selection@skills-dir`, a second copy beside the installed plugin.

For Codex, symlink the skill directory itself:

```bash
ln -s ~/code/hughescr/model-selection/skills/model-selection ~/.codex/skills/model-selection
```

# Credentials
The script reads the Artificial Analysis key from `ARTIFICIAL_ANALYSIS_API_KEY`. If that is unset and the 1Password
CLI `op` is on PATH, it runs `op read "$ARTIFICIAL_ANALYSIS_OP_REF"` (default
`op://Private/Artificial Analysis/credential`). There is no credentials file: a key file beside the skill would be
committed or synced with the plugin.

