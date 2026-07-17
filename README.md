# Skill for model selection
Why? So subagents can better select models based on real data.

How? It uses Artificial Analysis' API (sorry, you need to sign up for an account, but it's free)
This caches the API calls on a daily basis, so it doesn't blow the 100 req/day free tier limit. You're good.

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
Just clone the repo into your skills folder:

```bash
cd ~/.claude/skills

# Clone
git clone git@github.com:tkellogg/model-selection.git
```

If you use two agents, you can symlink it to the other:

```bash
cd ~/.codex/skills

ln -s ../../.claude/skills/model-selection model-selection
```


