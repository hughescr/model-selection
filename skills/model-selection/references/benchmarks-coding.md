# Coding Benchmarks

Use coding benchmarks to answer different questions. “Can the model write a correct function?”, “Can it modify a repository?”, “Can it operate a terminal?”, and “Can it produce scientific Python?” are separate capabilities. Artificial Analysis's [Intelligence Benchmarking Methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking) places Terminal-Bench v2.1 and SciCode in its current Coding category, while LiveCodeBench is a standalone evaluation. Its [Coding Agent Index methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking) evaluates end-to-end agents and should not be conflated with a model-only API score.

## Quick Decision Map

| Task shape | First metrics to inspect | Why |
| --- | --- | --- |
| Interactive coding agent using shell/tools | `artificial_analysis_coding_index`, `terminal_bench_v2_1`, coding-agent results | Terminal actions, execution, recovery, and environment interaction matter. |
| Fix an issue in an existing repository | SWE-bench family, DeepSWE, repository-level agent results | The task requires reading an unfamiliar codebase and producing a verified patch. |
| Generate algorithms or contest solutions | `livecodebench`, HumanEval-like fields | Correctness is usually executable, and fresh problems reduce contamination risk. |
| Scientific or numerical Python | `scicode`, `critpt` | Scientific background, implementation details, and test execution are central. |
| Code explanation or repository Q&A | `swe_atlas_qna` or task-specific evaluation | Answering questions is not the same as editing and testing code. |

## Artificial Analysis Coding Index

Artificial Analysis's composite is a summary of several evaluations and a useful first sort, not a complete coding score. The current public Coding Agent Index combines DeepSWE (long-horizon software engineering), Terminal-Bench v2 (agentic terminal use), and SWE-Atlas-QnA (repository Q&A). It aggregates task-level outcomes and efficiency metrics across a fixed harness. API model records may expose `artificial_analysis_coding_index` separately; inspect the raw field and its version before assuming it is the same composite.

**What it indicates:** broad performance under the specific Artificial Analysis coding harness and task mix.

**Strengths:** summarizes multiple coding modes; end-to-end task outcomes are closer to agent use than isolated code completion; per-evaluation results preserve some diagnostic detail.

**Shortcomings:** the harness, tools, context management, model settings, and timeouts influence the score; one composite can hide a model that is strong in code generation but weak at terminal recovery or repository Q&A; the API may expose a model-only coding index while the public coding-agent index measures a whole agent system.

**Use it when:** choosing a starting shortlist for an agentic coding workflow. Follow it with the benchmark matching the actual workflow and a small local acceptance test.

## Terminal-Bench v2.1

Source: [Artificial Analysis Terminal-Bench methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking), [Terminal-Bench](https://www.tbench.ai/), and [Terminal-Bench v2.1 paper](https://arxiv.org/abs/2601.11868).

**What it measures:** an agent's ability to complete 89 verified terminal tasks spanning software engineering, system administration, data processing, model training, and security. Artificial Analysis runs it with Terminus 2 in an E2B sandbox, requires every test in a task's verification suite to pass, and reports pass@1 averaged over three repeats.

**What a high score means:** the model and harness can plan and execute multi-step shell work, inspect state, use installed tools, and reach a tested end state under the benchmark's limits. It is particularly relevant to coding agents that can run commands.

**Pros:** executable verification rather than a language-model judge; broad terminal task mix; exposes tool use and recovery failures that code-only benchmarks miss.

**Cons and validity threats:** it is an agent-plus-harness result, not a pure model property; sandbox packages, permissions, tool wrappers, timeouts, and episode limits matter; all-tests-pass is unforgiving and can undercount useful partial progress; task coverage is not a representative sample of every developer workflow.

**Selection advice:** use it for agents that can operate a terminal. Pair it with repository repair results and a local test of the tools, languages, and conventions in the target codebase.

## SciCode

Source: [SciCode benchmark site](https://scicode-bench.github.io/), [paper](https://arxiv.org/abs/2407.13168), and [Artificial Analysis methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking).

**What it measures:** Python programming for scientific computing. Tasks include scientist-annotated background information and are evaluated by executing generated code. Artificial Analysis reports subproblem-level scoring with pass@1 rather than requiring every multi-part problem to be perfect.

**What a high score means:** the model can translate scientific descriptions and formulas into executable Python that passes the supplied checks. It says more about scientific implementation than generic prose or contest speed.

**Pros:** execution-based grading; domain context is part of the prompt; subproblem scoring gives more resolution than a single all-or-nothing task result.

**Cons and validity threats:** Python and the selected scientific domains are only a slice of software engineering; annotated background can make retrieval and problem framing easier than a real research setting; tests may reward expected implementations and do not guarantee scientific validity; performance depends on the supplied runtime and numerical tolerances.

**Selection advice:** prioritize it for notebooks, simulations, data analysis, and research code. Inspect it alongside Terminal-Bench when the work also requires environment setup, files, or shell tools.

## LiveCodeBench

Source: [official repository](https://github.com/LiveCodeBench/LiveCodeBench), [paper](https://arxiv.org/abs/2403.07974), and [Artificial Analysis's standalone methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking).

**What it measures:** code generation and related capabilities using newly collected problems from LeetCode, AtCoder, and Codeforces. The project also covers code execution, test-output prediction, and self-repair. Artificial Analysis uses Python code-generation scenarios, pass@1, and does not apply LiveCodeBench custom system prompts.

**What a high score means:** the model can produce a correct solution to relatively self-contained programming problems under the selected version and time window.

**Pros:** continuously refreshed problems make straightforward training-data contamination less likely; executable tests provide objective outcomes; broader than HumanEval-style one-shot generation.

**Cons and validity threats:** competitive-programming distributions overrepresent algorithmic puzzles and underrepresent maintenance, design, debugging, collaboration, and product constraints; scores change with dataset version and cutoff window; prompt formatting and language support matter; “contamination-free” is a design goal, not a proof that no overlap exists.

**Selection advice:** use it for algorithmic code generation and fresh-model comparisons. Do not use it as the sole reason to select a repository agent.

## SWE-bench and Variants

Source: [SWE-bench project](https://www.swebench.com/), [original benchmark paper](https://arxiv.org/abs/2310.06770), and [SWE-bench Verified discussion](https://openai.com/index/introducing-swe-bench-verified/).

**What it measures:** an agent receives a real GitHub issue and a repository, then must produce a patch that resolves the issue and passes the project's tests. Variants differ in task set, filtering, repository coverage, and harness.

**What a high score means:** under the specified agent scaffold, the system can understand a real issue, navigate a repository, edit code, and satisfy the evaluation tests on a single attempt.

**Pros:** realistic repository context; tests provide a concrete success condition; exposes long-context navigation, debugging, and patch synthesis.

**Cons and validity threats:** the agent scaffold can dominate the result; issue descriptions and test suites can be ambiguous or incomplete; tests can miss regressions or encode an implementation-specific solution; public tasks can contaminate training data; single-attempt pass rates omit the value of iterative human feedback; not all production work arrives as a well-specified GitHub issue.

**Selection advice:** compare only like-for-like variants and harnesses. Prefer recent, held-out, or decontaminated sets when models are close. Treat a benchmark win as evidence for repository repair, not a guarantee of design quality or safe code.

## Interpreting API Coding Fields

API field names vary by release. Common aliases used by the formatter are:

```text
artificial_analysis_coding_index
terminal_bench_v2_1, terminal_bench
scicode
livecodebench
swe_bench, deep_swe, swe_atlas_qna
bigcodebench, humaneval
```

Keep the original key and raw value in reports. A normalized pass rate such as `livecodebench: 0.717` is displayed as 71.7 by the helper, while an index such as `artificial_analysis_coding_index: 55.8` remains 55.8. These numbers are comparable for sorting only after labeling what each one means; they are not interchangeable probabilities of completing a user's task.

## Sources and Further Reading

- [LiveCodeBench official repository](https://github.com/LiveCodeBench/LiveCodeBench)
- [SWE-bench official project](https://www.swebench.com/)
- [SWE-bench Pro paper](https://arxiv.org/abs/2509.16941) for long-horizon enterprise-style task limitations
- [SWE-rebench paper](https://arxiv.org/abs/2505.20411) for continuously collected, decontaminated software-engineering evaluation
