# Writing, Knowledge, and Long Context

None of these is a pure writing-quality benchmark. Use them as different signals for professional deliverables, constraint compliance, document reasoning, factuality, and broad knowledge. For voice, originality, editing, audience fit, or tone, add a small human-rated task set.

## Quick Decision Map

| Task shape | First metrics | What it actually tells you |
| --- | --- | --- |
| Create professional documents, slides, spreadsheets, or reports | `gdpval_aa_v2`, `aa_briefcase` | Deliverable production plus research, analysis, formatting, and agent execution. |
| Long document synthesis | `aa_lcr` | Answer correctness over approximately 100K-token multi-document inputs. |
| Strict formatting or output contracts | `ifbench` | Machine-checkable instruction compliance. |
| Factuality and abstention | `aa_omniscience`, domain fields | Whether the model answers accurately and avoids incorrect guesses. |
| Broad academic knowledge | `mmlu_pro` | Multiple-choice knowledge/reasoning prior, not workplace execution. |
| Policy-grounded support/tool agent | `tau3_banking` | Retrieval, tool discovery, multi-step state changes, and backend success. |

## GDPval-AA v2

Source: [Artificial Analysis methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking), [GDPval paper](https://arxiv.org/html/2510.04374), [AA evaluation page](https://artificialanalysis.ai/evaluations/gdpval-aa).

**Measures:** economically valuable work across 44 occupations and nine industries, with deliverables such as documents, spreadsheets, slides, diagrams, and other professional artifacts. Artificial Analysis evaluates the public 220-task gold subset of the larger GDPval dataset.

**Protocol and score:** the agent runs in the Stirrup/E2B sandbox with code execution, web search/fetch, image viewing, and file submission, with up to 250 turns. Two submissions for a task are anonymously pairwise-judged by a panel of three frontier models. A Bradley-Terry maximum-likelihood model produces an Elo score anchored to human expert deliverables at 1,000.

**What a high score indicates:** the system can produce preferred professional deliverables under realistic instructions and tool access. It is a relative preference/Elo score, not an absolute correctness percentage.

**Pros:** broad occupational coverage; expert-created tasks; realistic file formats; tests analysis, calculation, formatting, instruction following, and artifact production together.

**Cons:** only a few tasks per occupation in the gold subset; pairwise LLM judging is subjective; the harness and tool behavior influence outcomes; tasks are mostly self-contained and one-shot rather than interactive. It is not a clean measure of prose quality.

**Use it for:** professional knowledge work and file-generating agents. Inspect deliverable or task breakdowns when available, and pair with a human writing rubric plus a long-horizon benchmark.

## AA-Briefcase

Source: [AA Briefcase article](https://artificialanalysis.ai/articles/aa-briefcase), [AA methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking), [public Lite dataset](https://huggingface.co/datasets/ArtificialAnalysis/AA-Briefcase-Lite).

**Measures:** long-horizon professional workflows across data science, product management, banking operations, and heavy-industry strategy. The full benchmark uses 91 tasks and thousands of source files such as email, Slack exports, spreadsheets, PDFs, transcripts, and business records.

**Protocol and score:** tasks run in an offline E2B sandbox for up to 500 turns. Rubric checks test requirements, evidence use, and conclusions; pairwise judgments cover analytical quality and presentation quality. The headline Elo combines rubric performance with analytical and presentation judgments.

**What a high score indicates:** the agent can find evidence across fragmented context, reason over messy inputs, create usable files, and present results professionally.

**Pros:** messy multi-file context; hidden requirements and contradictions; realistic professional deliverables; separates correctness, analysis, and presentation dimensions.

**Cons:** official tasks and rubrics are private; the public Lite dataset is illustrative and not the leaderboard; tasks run independently, so agents do not carry forward their own prior submissions; presentation judgments can reward polish without guaranteeing factual quality.

**Use it for:** memos, decks, research outputs, business analysis, and other deliverables over long trajectories. Give rubric pass rate more weight than aggregate Elo when correctness is critical. This is still not a pure writing test.

## AA-LCR

Source: [AA methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking), [AA-LCR article](https://artificialanalysis.ai/articles/announcing-aa-lcr), [dataset card](https://huggingface.co/datasets/ArtificialAnalysis/AA-LCR).

**Measures:** reasoning across multiple long documents. The benchmark has 100 hard questions spanning company, industry, government, academic, legal, marketing, and survey documents, with approximately 100K input tokens per question.

**Protocol and score:** open answers are judged equivalent or not equivalent to reference answers by an equality-checker LLM. Artificial Analysis reports pass@1 with three repeats and averages the pass rate. The stated setup requires a minimum 128K context window.

**What a high score indicates:** the model can retrieve, connect, and synthesize information distributed across a long input.

**Pros:** real-world document types; multi-document reasoning; relevant to legal, financial, policy, and research analysis.

**Cons:** only 100 questions; a mostly fixed approximately 100K regime rather than a full context curve; equality checking misses nuanced answer quality; no tools, interaction, or artifact production; public documents can eventually contaminate training data.

**Use it for:** a long-context gate. Pair it with retrieval/tool evaluation when the production system must search a corpus instead of receiving the full corpus directly. Do not infer prose quality from the score.

## AA-Omniscience

Source: [AA methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking), [AA paper](https://arxiv.org/html/2511.13029), [AA evaluation page](https://artificialanalysis.ai/evaluations/omniscience).

**Measures:** closed-book factual recall and calibration over 6,000 questions, 42 topics, and business, humanities/social sciences, health, law, software engineering, and science/engineering/mathematics.

**Protocol and score:** models answer without tools and may abstain when uncertain. Responses are classified as `CORRECT`, `PARTIALLY_CORRECT`, `INCORRECT`, or `NOT_ATTEMPTED`. The Omniscience Index is approximately `100 * (correct - incorrect) / all_questions`; accuracy and hallucination rate should be inspected alongside it. Grader versions have changed, so historical scores require protocol labels.

**What a high score indicates:** reliable closed-book knowledge and a lower tendency to guess incorrectly. Positive index values mean correct answers outnumber incorrect answers.

**Pros:** explicit hallucination penalty; domain breakdowns; distinguishes accuracy from calibration; useful for deciding whether to answer directly or defer to search/tools.

**Cons:** not writing, retrieval, supplied-context reasoning, or tool use; English and source-selection bias; automated question generation and grader choice can introduce model-family bias; an always-abstaining model can score zero, so attempt rate matters.

**Use it for:** factuality-sensitive applications. Prefer low hallucination rate for high-stakes workflows and inspect the domain relevant to the application instead of using raw accuracy alone.

## IFBench

Source: [IFBench paper](https://arxiv.org/abs/2507.02833), [official repository](https://github.com/allenai/IFBench), [AA methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking).

**Measures:** generalization to unseen, precisely verifiable output constraints such as counting, ratios, word/sentence manipulation, formatting, copying, and structured requirements.

**Protocol and score:** the official evaluator computes strict and loose constraint compliance. Artificial Analysis uses 294 single-turn questions, five repeats, pass@1, and prompt-level accuracy, where every constraint in a prompt must pass. Its loose mode allows limited normalization such as removing wrapper lines or asterisks; it does not use the multi-turn version.

**What a high score indicates:** the model can obey unusual machine-checkable requirements on the first attempt.

**Pros:** reproducible programmatic verification; useful for schemas, formatting contracts, and output validators; tests constraint generalization rather than only ordinary instruction following.

**Cons:** constraints can be artificial and can compete with task usefulness; public constraints may be overfit; loose scoring can hide wrapper behavior that matters operationally; it does not measure correctness, coherence, or prose quality.

**Use it for:** structured-output and compliance gates. Pair it with GDPval or Briefcase to make sure formatting obedience does not replace useful work.

## MMLU-Pro

Source: [MMLU-Pro paper](https://arxiv.org/abs/2406.01574), [official repository](https://github.com/TIGER-AI-Lab/MMLU-Pro), [AA methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking).

**Measures:** broad academic and professional knowledge/reasoning across 14 domains and more than 12,000 questions. It expands original MMLU from four to ten choices and removes some trivial or noisy items.

**Protocol and score:** ten-option multiple choice, regex answer extraction, and pass@1. Artificial Analysis currently reports 12,032 questions with one repeat.

**What a high score indicates:** a useful broad prior for academic knowledge and multi-step question reasoning.

**Pros:** wide subject coverage; harder and more discriminative than original MMLU; ten choices reduce guessing.

**Cons:** multiple choice limits depth and realism; no file production, interaction, or tools; academic content may not match a business domain; public data contamination is a practical concern.

**Use it for:** a broad knowledge/reasoning tie-breaker or domain screen. Do not select a writing or agent model from MMLU-Pro alone.

## tau3-Banking / tau-Knowledge

Source: [AA methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking), [AA tau3-Banking page](https://artificialanalysis.ai/evaluations/tau3-banking), [tau-Knowledge paper](https://arxiv.org/html/2603.04370), [official repository](https://github.com/sierra-research/tau2-bench).

**Measures:** conversational banking agents that retrieve policy from a large unstructured corpus, reason over customer state, discover tools documented only in the corpus, and execute account changes. The AA suite uses 97 tasks, roughly 700 policy documents and 195K tokens, 21 product categories, and backend-state grading.

**Protocol and score:** multi-turn agent-user simulation with search/retrieval and state-changing tools. Success is determined by the final database state rather than conversational quality. Artificial Analysis uses five repeats per task, with 200-step and 10-tool-error limits.

**What a high score indicates:** reliable policy-grounded tool use in this banking-support environment.

**Pros:** objective backend verification; realistic policy/tool coupling; multi-step dependencies; exposes retrieval and state-change failures.

**Cons:** narrow fintech domain; simulated users and policy corpus; retrieval configuration and harness matter; backend success does not measure empathy, clarity, or writing quality; deployment latency and generalization remain open questions.

**Use it for:** customer-support, operations, and policy-constrained agents. Compare identical retrieval and simulator settings, and prefer repeated-trial reliability or cost-per-success over pass@1 alone.

## Selection Recipe

- Professional deliverables: GDPval-AA v2 plus AA-Briefcase.
- Long document analysis: AA-LCR plus a retrieval benchmark if search is required.
- Strict schemas and formatting: IFBench.
- Factuality and abstention: AA-Omniscience plus domain-specific tests.
- Broad academic knowledge: MMLU-Pro as a prior, not a final decision.
- Policy-grounded tools: tau3-Banking.
- Pure writing quality: human-rate representative prompts for audience fit, clarity, structure, factuality, tone, editing, and revision behavior.

Do not average these raw scores together. Use them as capability gates and Pareto dimensions alongside internal tasks, cost, latency, and repeated-trial reliability.
