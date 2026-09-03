# Case study 1: virtual screening under a fixed budget

## Research question

How should an automated system allocate expensive molecular inference when the evaluation input is new, the workload is large, the hardware throughput is not known in advance, and every row still has to be delivered in the original order?

This was primarily a **measurement and scheduling** problem around a specialized scientific scorer—not a claim that an LLM invented a new screening model at runtime.

## Historical result

- Best recorded platform Mean EF1%: `39.69658`, reported as `39.70`.
- Normalized score: `0.8095`.
- The best result is associated with the v200 line.
- A later audit-material correction ran `39.63083`; it did not replace the best-scoring version’s identity.

## Runtime control loop

```mermaid
flowchart LR
    A["Discover mounted input"] --> B["Validate task and row contract"]
    B --> C["Create full-coverage 2D floor"]
    C --> D["Warm up and measure 3D throughput"]
    D --> E["Allocate expensive scoring depth"]
    E --> F["Run specialized molecular scorer"]
    F --> G["Fuse or fall back"]
    G --> H["Check target count, row order, duplicates, finite values"]
    H --> I["Write and verify archive atomically"]
```

The evaluated workload was large enough that full expensive inference could not be assumed. The system had to reserve enough time for complete packaging and output persistence, not spend the final second on inference.

## What changed at runtime

- where and when the mounted input became visible;
- task and ligand counts;
- available CPU/GPU resources;
- measured warm-up throughput;
- remaining time and the resulting expensive-scoring coverage;
- failures that forced a cheaper fallback.

## What was fixed before runtime

- the scientific scoring model and weights;
- the candidate strategy family and fusion logic;
- the cheap full-coverage floor;
- the scheduler structure and fallback paths;
- output schema, ordering checks, and packaging behavior.

The most accurate autonomy label is **bounded decision support plus a measurement-driven executor**.

## Why measurement mattered

An early engineering pattern tried to infer feasibility from configuration and local expectations. Platform behavior showed that the important variables were observable only at runtime: mount readiness, actual model initialization, real molecules per second, and output-persistence delay.

A useful scheduling equation is:

```text
available_inference_time = deadline - now - delivery_reserve
affordable_work = measured_throughput × available_inference_time
```

The delivery reserve is part of the scientific system because a high-quality partial computation that is killed before a valid artifact is committed has no usable result.

## Evidence chain

| Claim | Best evidence | Boundary |
|---|---|---|
| Input was processed at scale | runtime coverage and packaging records | raw records are not redistributed |
| Expensive inference depth changed with throughput | scheduler code path + runtime stage records | does not prove optimal allocation |
| Final artifact was structurally valid | row/ordering/duplicate/finite checks | does not establish screening science |
| v200 received `39.69658` | platform result bound to historical version line | public repository is not the scoring image |

## Representative negative lessons

1. **Input discovery can dominate the entire run.** A container can start successfully while remote-mounted data is not yet enumerable. A robust system needs bounded readiness checks and direct contract probes, not optimistic directory listing.
2. **Output delivery is not clerical work.** Temporary files, flush, atomic replace, archive validation, and exit margin decide whether the platform sees a valid result.
3. **“Smarter” preprocessing can regress.** A local parameter sweep showed a more aggressive conformer iteration setting increased failure rate without improving effective throughput; the change was reverted.
4. **A configuration fallback can silently change the method.** One historical regression came from missing fusion defaults that allowed an unintended signal to dominate. Observability of effective runtime weights was added after the failure.

## What this case does not prove

- that the public repository redistributes or reproduces the historical scorer;
- that an LLM caused the `39.70` result;
- that EF1% guarantees experimental activity;
- that one scheduler is optimal for all screening distributions or hardware.

## Public reconstruction level

- **R1:** this control and evidence narrative is reviewable.
- **R2:** the public core verifies only the generic floor → experiment → validate → rollback discipline; throughput allocation itself remains R1 narrative.
- **R3/R4:** not claimed for the historical molecular stack or platform score.
