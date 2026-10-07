# Math and Scientific Reasoning

Artificial Analysis Intelligence Index v4.1 places HLE, GPQA Diamond, and CritPt in Scientific Reasoning with 12%, 6%, and 6% weights respectively. MATH-500 and AIME 2025 are legacy evaluations and are no longer active index components. The current suite is text-only and English-only, and individual benchmark uncertainty can be wider than the aggregate index. Source: [Artificial Analysis methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking).

## Quick Decision Map

| Task shape | First metric | Read it as |
| --- | --- | --- |
| Broad difficult academic questions | `hle` | Breadth across math, humanities, and natural sciences. |
| Graduate biology, chemistry, or physics | `gpqa` | Closed-book STEM knowledge plus hard multiple-choice reasoning. |
| Physics research assistant | `critpt` | Multi-step research-style physics and precise answer production. |
| General math regression | `math_500` | Public competition-math final-answer correctness. |
| Contest-math discrimination | `aime_2025`, `aime` | Difficult integer-answer competition problems. |
| Scientific Python implementation | `scicode` | See [coding benchmarks](benchmarks-coding.md), because SciCode is a coding evaluation. |

## Humanity's Last Exam (HLE)

Source: [AA HLE evaluation](https://artificialanalysis.ai/evaluations/humanitys-last-exam), [HLE paper](https://arxiv.org/html/2501.14249v5), [HLE dataset](https://huggingface.co/datasets/cais/hle).

**Measures:** 2,158 text-only questions from the May 2025 HLE revision across mathematics, humanities, and natural sciences. The broader revision contains multimodal questions; Artificial Analysis excludes images for comparability.

**Protocol and score:** zero-shot, closed-book questions with structured final answers. Artificial Analysis uses pass@1 and an equality-checker LLM for semantic equivalence, with small numerical tolerances. Headline score is correctness, not calibration.

**What a high score indicates:** broad, difficult closed-ended academic competence, specialized knowledge retrieval, and exact answer production.

**Pros:** broad coverage; expert-authored questions; multiple review rounds; frontier difficulty; exact or multiple-choice answers; intended private holdouts for overfitting checks.

**Cons and validity threats:** HLE deliberately selects questions that stump named frontier models, which creates model-dependent selection bias. Reviewers were not expected to fully verify very long rationales, and small score movements can reflect inference noise. External audits have reported answer conflicts with published literature in parts of the dataset; treat those as audit findings rather than assuming every item is ground truth.

**Use it for:** a broad academic capability gate under the exact same revision, grader, prompt, and inference settings. Track subject-level performance and confidence/calibration separately. Do not call it a universal reasoning score or infer interactive research ability.

## GPQA Diamond

Source: [AA GPQA evaluation](https://artificialanalysis.ai/evaluations/gpqa-diamond), [GPQA paper](https://arxiv.org/abs/2311.12022), [official repository](https://github.com/idavidrein/gpqa).

**Measures:** 198 four-option questions in biology, physics, and chemistry. The Diamond subset was selected for maximum difficulty and discriminative power, requiring expert agreement and majority non-expert failure.

**Protocol and score:** zero-shot multiple-choice prompting, regex answer extraction, five repeats, and pass@1 aggregation. Chance is 25%; there is no partial credit or reasoning-process score.

**What a high score indicates:** difficult closed-book scientific knowledge and multi-step reasoning under distractors, especially in the three covered STEM domains.

**Pros:** expert-written questions; strong expert/non-expert separation; deterministic answer-key scoring; useful frontier discriminator.

**Cons and validity threats:** selected Diamond items are not representative science; only three disciplines; small 198-item sample makes small gaps noisy; multiple choice measures answer selection rather than reasoning quality; “Google-proof” validation predates modern search agents and does not rule out memorization or data leakage.

**Use it for:** a science-domain gate. Compare by domain and use uncertainty intervals when models are close. Pair with HLE for breadth and CritPt or fresh domain tasks for open-ended scientific reasoning. Do not infer web research or scientific discovery ability.

## CritPt

Source: [AA CritPt evaluation](https://artificialanalysis.ai/evaluations/critpt), [CritPt paper](https://arxiv.org/html/2509.26574v3), [repository and grader](https://github.com/CritPt-Benchmark/CritPt).

**Measures:** research-style physics challenges. CritPt contains 71 composite challenges and 190 checkpoints across 11 physics areas; one example is public, leaving 70 test challenges. Problems are authored by active researchers and designed to be unpublished, self-contained, search-resistant, and guess-resistant.

**Protocol and score:** Artificial Analysis evaluates 70 challenges, runs five repeats with pass@1, and makes two model calls: one for the solution and one to format the final answer. The official grader supports numerical values, SymPy expressions, and Python functions tested against expert-selected cases; composite answers require every component to pass.

**What a high score indicates:** end-to-end research-style physics reasoning, mathematical execution, precision, and coherent multi-step problem solving.

**Pros:** fresh difficult data; domain-expert curation; search-resistant construction; machine-verifiable outputs; multiple answer types; composite tasks reveal failures hidden by isolated questions.

**Cons and validity threats:** only 70 challenges with uneven subfield coverage; “research-level” means warm-up work for junior researchers, not autonomous discovery; final-answer grading can miss invalid reasoning that reaches the right answer; the two-call parsing protocol adds formatting effects; five samples are not statistically sufficient for strong consistency claims; the standard run has no tools even though tools matter in real scientific work.

**Use it for:** physics, scientific computing, or research-assistant selection. Prefer full-challenge results for end-to-end choices; use checkpoint results for decomposition and expert-verification workflows. Do not treat CritPt as general reasoning outside scientific physics.

## Legacy MATH-500

Source: [AA MATH-500 evaluation](https://artificialanalysis.ai/evaluations/math-500), [MATH paper](https://arxiv.org/abs/2103.03874), [OpenAI PRM800K grader](https://github.com/openai/prm800k), [dataset card](https://huggingface.co/datasets/HuggingFaceH4/MATH-500).

**Measures:** 500 high-school competition-math problems across algebra, geometry, number theory, counting, and related subjects. It is a subset of the MATH test set.

**Protocol and score:** final-answer correctness with normalized exact-answer comparison; the reference grader uses SymPy equivalence checks but documents occasional false accepts/rejects. Artificial Analysis's legacy page is not a promise that current index protocol is unchanged.

**What a high score indicates:** broad competition-math final-answer skill and symbolic manipulation.

**Pros:** larger and more diverse than AIME; cheap to run; mostly deterministic; useful for regression tests.

**Cons and validity threats:** public and contamination-prone; final answer does not validate proof or reasoning; split conventions complicate comparisons; increasingly saturated for frontier models.

**Use it for:** a math sanity check or regression, especially for smaller/cost-sensitive models. Pair with fresh or private problems for current frontier selection.

## Legacy AIME 2025

Source: [AA AIME 2025 evaluation](https://artificialanalysis.ai/evaluations/aime-2025), [MAA AIME description](https://maa.org/maa-invitational-competitions/), [contamination analysis](https://arxiv.org/abs/2505.23281).

**Measures:** 30 integer-answer problems, combining AIME I and II 2025. Each answer is a three-digit integer from `000` to `999`.

**Protocol and score:** step-by-step prompts with boxed final answer, 10 repeats per question, and pass@1 aggregation. Script grading uses SymPy normalization with an equality-checker fallback. No partial credit.

**What a high score indicates:** difficult high-school competition-math insight and precise multi-step calculation.

**Pros:** high-quality and sharply discriminative; strict easy-to-read output format.

**Cons and validity threats:** only 30 questions, so one item is roughly 3.3 percentage points before repeat averaging; public items can leak; final-answer scoring can reward memorization or brute force without proof; it is retired from active index reporting.

**Use it for:** a secondary math gate or cost/accuracy diagnostic. Require fresh post-release or private corroboration and report the exact version, repeat policy, reasoning budget, and tool policy.

## Practical Policy

- Broad academic breadth: HLE.
- Graduate STEM knowledge: GPQA Diamond.
- Physics research assistance: CritPt.
- General math regression: MATH-500.
- Contest-math discrimination: AIME 2025.

Keep score, cost, repeat variance, and contamination status separate. None of these directly tests interactive planning, tool-use reliability, proof quality, or real-world task completion.
