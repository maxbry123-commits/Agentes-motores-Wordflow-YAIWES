# Third-party notices and redistribution boundary

This document records systems discussed by the case studies. **No source code, model weights, official datasets, or binary packages from these systems are redistributed by this repository unless the current file manifest explicitly says otherwise.** A project’s source-code license does not automatically cover its weights, training data, templates, stock databases, online services, or nested dependencies.

The links and license notes below are orientation, not legal advice. Anyone building a scientific adapter must pin the exact version and re-check the applicable code, weight, and data terms.

## Virtual screening

| Component | Role in the historical project | Public treatment |
|---|---|---|
| [LigUnity](https://idea-xl.github.io/LigUnity/) | Scientific scoring backend in the best recorded task1 path | Referenced only. Exact local source/weight provenance and redistribution rights were not closed, so no snapshot or weight is published. |
| [Uni-Mol](https://github.com/deepmodeling/Uni-Mol) | Molecular representation dependency in the historical stack | Upstream currently describes code under MIT; exact historical commit and weight terms still require separate verification. Not vendored here. |

## Molecule design and retrosynthesis

| Component | Role in the historical project | Public treatment |
|---|---|---|
| [AutoDock Vina](https://github.com/ccsb-scripps/AutoDock-Vina) | Higher-fidelity CPU docking and review path | Upstream code is described under Apache-2.0. This repository provides no Vina binary or docking data. |
| [Uni-Dock](https://github.com/dptech-corp/Uni-Dock) | GPU exploration docking | Current upstream source is described under Apache-2.0; the exact historical image version and nested assets still require separate verification. Not vendored here. |
| [AiZynthFinder](https://github.com/MolecularAI/aizynthfinder) | Retrosynthesis route search | Upstream code is described under MIT, while policy models, stocks, templates, and other data have separate provenance. None are redistributed here. |
| [DiffSBDD](https://github.com/arneschneuing/DiffSBDD) | An explored candidate-generation route, not a stable public path | Upstream source is described under MIT; exact local source and checkpoint provenance remained unresolved. Excluded. |
| [RDKit](https://github.com/rdkit/rdkit) | Molecular parsing and deterministic chemistry checks | Upstream source is described under BSD-3-Clause. No RDKit source or binary is vendored here. |

## Protein ensembles

| Component | Role in the historical project | Public treatment |
|---|---|---|
| [Boltz](https://github.com/jwohlwend/boltz) | Structure-generation engine | Upstream describes code and published weights under MIT. This repository does not redistribute them; users must review the selected release. |
| [AlphaFlow](https://github.com/bjing2016/alphaflow) | Conformational sampling route | Upstream code is described under MIT but includes or depends on components with separate terms. Not vendored. |
| [OpenFold](https://github.com/aqlaboratory/openfold) | Part of the AlphaFlow/OpenFold stack | Upstream source is described under Apache-2.0; model parameters and nested dependencies are separate objects. Not redistributed. |
| AlphaFold parameters | Parameters used by parts of the ecosystem | Upstream documentation identifies CC BY 4.0 terms for relevant parameters. No parameters are included here. |
| [BioEmu](https://github.com/microsoft/bioemu) | Explored but not retained as the stable final path | Upstream source is described under MIT; weights and data remain separate assets. Negative-result discussion links upstream only. |

## Neural-operator PDE work

Official models, checkpoints, datasets, evaluator code, and competition attachments used by the historical task are excluded. The public case study discusses the governance failure and exposes only personal, task-agnostic control patterns. It does not publish the two ruled-out task-specific training tools.

## Language-model and online services

Development-time programming agents and runtime language-model services were used in different roles and changed across versions. No model service, client credential, private endpoint, response log, or provider-specific payload is redistributed. A runtime model is a replaceable control dependency, not the owner of the scientific backend output or an automatic explanation of a platform score.

## Competition materials

Official problem statements, authenticated downloads, hidden inputs, platform outputs, scoring images, review packages, and submission archives are not licensed by this repository and are not included.

## Apache-2.0 scope

The root [LICENSE](LICENSE) applies only to original code and documentation created for this personal repository. It does not relicense any item described above, any historical competition artifact outside this repository, or material owned by competition organizers.
