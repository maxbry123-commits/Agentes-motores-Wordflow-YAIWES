# Problem framing

## Competition setting

The project addressed four AI for Science tracks under fixed evaluation time and hardware. Each submission had to run without human intervention after the evaluation container started, process new mounted inputs, produce strict output artifacts, and leave auditable records.

The tracks covered:

1. high-throughput virtual screening;
2. targeted molecule design with retrosynthesis;
3. protein conformational ensembles;
4. neural-operator prediction for PDE systems.

The final competition ranking used the two strongest normalized tracks. This made track choice and robustness part of the research problem: a system that produced no valid artifact was worse than a lower-scoring valid floor.

## Initial misconception

An early project-level narrative was too broad:

> one common Agent reads the task, invents a method, writes code, evaluates it, and iterates across four domains.

The implementation record did not support that claim. What actually transferred was thinner and more useful:

- task and output contracts;
- bounded runtime observations;
- time and compute budgeting;
- tool-call records;
- failure classification and fallback;
- validation and atomic delivery;
- version and evidence discipline.

The scientific representations, models, evaluators, search spaces, and decision depth remained task-specific.

## Research questions

The four tasks became four different agent-control questions:

| Task | Control question |
|---|---|
| Virtual screening | How should measured throughput determine expensive-inference coverage? |
| Molecule design | Can current-target docking feedback change the next generation? |
| Protein ensemble | How should multiple generators, quality, diversity, randomness, and budget be balanced? |
| Neural operator | Where is the boundary between an atomic tool and a prewritten scientific solution? |

## Success criteria

A convincing project needed more than a score:

- **closed-loop behavior:** observation changes action;
- **scientific grounding:** real tools, not only LLM self-evaluation;
- **generalization discipline:** no hidden test-specific rules or data;
- **delivery robustness:** valid outputs under failure and timeout;
- **auditability:** claims tied to versions, events, tools, validators, and platform records;
- **honest limits:** unsupported causal claims remain unsupported.

## Two timelines that must not be mixed

### Development timeline

Humans and development-time programming agents selected tools, built pipelines, interpreted failures, wrote tests, and chose versions.

### Evaluation runtime

The submitted system processed new inputs, made bounded decisions where implemented, ran scientific tools, validated results, and delivered artifacts without human interaction after launch.

Zero manual runtime does not mean zero human design.
