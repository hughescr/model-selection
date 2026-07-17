# Agents, Composite Indices, and Cross-Cutting Reasoning

Use this file when the request is about agents, tool use, broad intelligence, benchmark aggregation, or why benchmark results disagree. The central rule is that an evaluation result belongs to a protocol: model, prompt, tool set, harness, dataset version, judge, turn budget, and retry policy. A score without that context is easy to overinterpret.

## Artificial Analysis Intelligence Index v4.1

Source: [Artificial Analysis Intelligence Benchmarking Methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking).

The current composite uses four categories:

| Category | Weight | Current evaluations |
| --- | ---: | --- |
| Agents | 34% | GDPval-AA v2, tau3-Banking |
| Coding | 24% | Terminal-Bench v2.1, SciCode |
| Scientific Reasoning | 24% | HLE, GPQA Diamond, CritPt |
| General | 18% | AA-LCR, AA-Omniscience |

Artificial Analysis describes the index as a synthesis of language-model capability, not a universal task-success probability. It is text-only and English-only. Its reported aggregate uncertainty is estimated below plus or minus 1% at a 95% confidence interval under its repeated-measure experiments, but individual evaluations can be much noisier.

**What a high score indicates:** broad performance on the exact mix of agentic work, coding, scientific reasoning, long-context reasoning, knowledge, and factuality chosen by Artificial Analysis.

**Pros:** avoids over-relying on one task family; publishes category and evaluation weights; exposes per-evaluation fields; gives a useful starting point when the task is genuinely broad.

**Cons and validity threats:** the 34% agent weight makes the result sensitive to a small number of agent harnesses; category weights encode a value judgment; benchmarks have different scales and graders; index versions change, including component replacement and weight changes; model release date, tool access, and inference settings can interact with contamination and capability.

**Selection advice:** use it as a broad shortlist ranker. For a real task, replace or supplement its category weights with the benchmark that matches the task. Report the index version and retrieval date, and retain the raw evaluation breakdown.

## Agent Benchmarks Are System Benchmarks

Agent evaluations generally measure `model + prompt + tool interface + harness + environment + policy + evaluator`, not the model in isolation. This is a feature for deployment prediction and a limitation for model-only attribution.

Check these dimensions before comparing two results:

- Are tools, retrieval, web access, and file parsers identical?
- Is the model allowed to use a different number of turns, context resets, or retries?
- Is the environment deterministic, networked, or dependent on external packages?
- Is success verified by tests/backend state, a rubric, or a language-model judge?
- Is the score pass@1, pass@k, pass^k, a pairwise Elo, or an average over repeats?
- Are costs and token counts for the model only, or for every tool and retry in the agent trajectory?

When a user asks “which model is best for my agent,” preserve the agent scaffold as part of the answer. A strong model in a weak harness can lose to a weaker model in a better harness, and a model ranking can change when the harness changes.

## GDPval-AA v2 and Knowledge Work

See [Writing and Knowledge Work](benchmarks-writing-knowledge.md) for the detailed benchmark entry. For agent selection, remember that GDPval uses an E2B sandbox, file outputs, web and code tools, up to 250 turns, anonymous pairwise judging, and Elo anchored to human experts. Its score indicates preferred deliverables under that workflow, not just language fluency or factual accuracy.

## tau3-Banking and Tool Use

See [Writing and Knowledge Work](benchmarks-writing-knowledge.md) for the protocol. The useful cross-cutting property is backend-state grading: an agent must retrieve policy, sequence tools, and leave the simulated account in the correct state. This is stronger evidence of reliable state-changing tool use than a judge saying that a conversation sounds helpful. It is still a narrow banking simulation, so combine it with a domain-matched internal test.

## Coding Agent Index

Source: [Artificial Analysis Coding Agent Index methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking).

The public coding-agent index currently aggregates DeepSWE long-horizon software engineering, Terminal-Bench v2 agentic terminal use, and SWE-Atlas-QnA repository questions. The stated purpose is to preserve per-benchmark differences while providing an outcome, reliability, token, cost, and execution-time summary.

**What a high score indicates:** the tested coding agent system handles a broad mix of repository changes, terminal work, and repository Q&A under the public suite.

**Pros:** recognizes that coding agents have multiple modes; includes efficiency dimensions; task-level results are more diagnostic than a single headline score.

**Cons:** agent scaffold and runtime are part of the score; the index can hide a model's mode-specific weakness; public task suites can be contaminated; it does not directly test a user's repository, language mix, review standards, or deployment process.

**Selection advice:** use the index for an agent shortlist, then inspect DeepSWE, Terminal-Bench, and Q&A separately. Match the winner to the user's actual interaction pattern, not to the aggregate alone.

## Judge and Grading Effects

**Executable grading:** tests or backend state are usually more objective, but they can be incomplete, brittle, over-specific, or environment-dependent. All-tests-pass can hide partial value and a missing test can hide a regression.

**Rubric grading:** makes professional artifacts and nuanced work scorable, but rubric interpretation and judge consistency matter. A rubric can reward presentation polish or a benchmark's preferred workflow.

**Pairwise Elo:** useful when absolute correctness is hard to define and human anchoring is available. Elo is relative; a 1,100 score is not “10% better” than 1,000, and a change in the comparison pool or judge can move rankings.

**LLM judges:** are cheaper and more flexible than expert grading, but can favor verbosity, formatting, familiar styles, or their own model family. Blinding, multiple judges, fixed graders, and task-level audits reduce but do not remove this risk.

## Contamination and Freshness

Static public benchmarks can enter training data, be memorized, or be indirectly leaked through solutions and discussion. Fresh-dated evaluations such as LiveCodeBench are designed to reduce direct contamination; private or post-cutoff tasks provide stronger evidence but are harder to reproduce. A benchmark's claim of contamination resistance is not a proof of zero overlap.

Treat the following as warning signs:

- large score gaps on old public tasks but small gaps on fresh/private tasks;
- sudden performance discontinuities near a model's cutoff date;
- scores that depend heavily on exact prompt wrappers or answer extraction;
- evaluations where the task set, gold patches, or solution discussions are public;
- comparisons that mix dataset revisions or judge versions without labeling them.

## Decision Policy

Use a constrained Pareto choice:

1. Filter to models the current runtime can actually invoke, or label the shortlist as “catalog only.”
2. Apply hard gates for task fit, required context, modality, tool support, and maximum cost.
3. Rank the survivors by the task-specific benchmark, not by the broad index.
4. Inspect the next two or three benchmark dimensions for regressions, missing data, or protocol mismatch.
5. Use cost, latency, output speed, and repeated-trial reliability as tie-breakers.
6. Validate the final two or three on a small representative local set before a high-stakes choice.

The skill's cost-per-intelligence ratio is `blended_price / selected_score`. It is useful for a rough frontier plot, but it is not cost per successful task. For agents, compute or estimate cost per successful completion when trajectory data is available; a cheap model that needs retries can be more expensive operationally.

## What to Say in a Recommendation

State:

- the task profile and hard constraints;
- which runtime evidence makes each model selectable;
- the benchmark and protocol used as the primary signal;
- the strongest counter-signal or missing metric;
- blended price, speed, and expected task-cost caveats;
- whether the evidence is model-only, agent-system, judge-based, executable, public, or fresh;
- the smallest local test that would resolve remaining uncertainty.

Avoid phrases such as “best model overall,” “human-level,” or “will solve your codebase” unless the evidence and scope truly support them.
