<div align="center">
  <img src="docs/assets/logo.jpeg" width="45%" alt="Yunjue Tech" />
</div>

<br> 


<div align="center">

[![BLOG](https://img.shields.io/badge/Blog-4285F4?style=for-the-badge&logo=google-chrome&logoColor=white)](https://www.yunjuetech.com/en)
[![Project HomePage](https://img.shields.io/badge/Project%20HomePage-00A86B?style=for-the-badge&logo=google-chrome&logoColor=white)](https://www.yunjuetech.com/Yunjue-Agent/)
[![GITHUB](https://img.shields.io/badge/Github-24292F?style=for-the-badge&logo=github&logoColor=white)](https://github.com/YunjueTech/Yunjue-Agent)
[![Paper](https://img.shields.io/badge/Paper-De2c33?style=for-the-badge&logo=adobe-acrobat-reader&logoColor=white)](https://arxiv.org/abs/2601.18226)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-blue?style=for-the-badge)](https://huggingface.co/datasets/YunjueTech/Yunjue-Agent-Traces)

</div>

<div align="center">

### [English](README.md)｜[中文](README_zh.md)

</div>


---

This repo is an official implementation of Yunjue Agent by Yunjue Technology. Our company is a cutting-edge technology company dedicated to building Self-Evolving AGI (Artificial General Intelligence) and wearable devices. We are a group of tireless explorers, with members from top AI laboratories and engineering teams. We are not satisfied with "static" large models—those with parameter matrices frozen after training completion. We believe that true intelligence lies not only in how much past knowledge is stored, but in the ability to adapt, learn, and create tools when facing an unknown future.

We welcome connections of all kinds. For financing inquiries, technical exchanges, or to join our team, please contact qiweizhen@yunjuetech.com

## 📰 News & Updates

- **[2026-01-26]** 🎉 **Initial Release**: We have open-sourced the **Yunjue Agent** system!
- **[2026-01-31]** 📦 **Data Release**: We released the system logs under **zero-start settings** for five benchmark datasets (**HLE**, **DeepSearchQA**, **FinSearchComp (T2&T3)**, **xbench-ScienceQA** and **xbench-DeepSearch**): [Google Drive](https://drive.google.com/drive/folders/1mL5PqKZwOUVIP-UYg0bZr11fotpZmcqb?usp=sharing). New: [Huggingface Dataset for one line code analysis](https://huggingface.co/datasets/YunjueTech/Yunjue-Agent-Traces).
- **[2026-01-31]** ✨ **Reproduction & Evaluation Update**: We organized the evaluation script and reproduction workflow (see [Reproducing Results](#-reproducing-results) below).
- **[2026-02-08]** 📄 **Tech Report Update**: We updated the tech report, adding more theoretical and experimental analysis on system performance, cost, and Evolutionary Generality Loss (EGL). You can access it via [arXiv](https://arxiv.org/abs/2601.18226) or the [local PDF](tech_report/YunjueAgentTechReport.pdf).
- **[2026-02-11]** 🔀 **Reproduction Branch Update**: We migrated reproduction to a dedicated stable branch: [reproduce](https://github.com/YunjueTech/Yunjue-Agent/tree/reproduce).
- **[2026-02-11]** 🎬 **Demo Release**: We implemented two demos (Web Demo and CLI Skill Demo). See [Demo Quick Start](#-demo-quick-start) below.


---

## 🚀 Quick Start

### 📋 Prerequisites

- **Python**: 3.12 or higher
- **Package Manager**: [`uv`](https://docs.astral.sh/uv/)
- **Operating System**: MacOS

### ⚡ Quick Setup

```bash
# 1. Clone and setup
git clone https://github.com/YunjueTech/Yunjue-Agent.git && cd Yunjue-Agent

chmod +x install.sh

./install.sh

# NOTE: `install.sh` installs the `codex` CLI, but you still need to configure Codex yourself
# (e.g., set `OPENAI_API_KEY` and optionally `CODEX_PROFILE` in your environment).
cp .env.example .env

cp conf.yaml.example conf.yaml

source .venv/bin/activate
```

### ⚙️ Configuration

- **Configuration reference**: see `docs/configuration_reference.md` for the meaning of key fields in `.env` (e.g., `TAVILY_API_KEY`, `MAX_WORKER_RECURSION_LIMIT`, `MAX_TASK_EXECUTION_CNT`, `PROXY_URL`) and `conf.yaml` (e.g., `VISION_MODEL`, `SUMMARIZE_MODEL`).
- **Config templates**: start from `.env.example` and `conf.yaml.example`.

### 🧪 Reproducing Results

- We have migrated reproduction to a stable branch for reproducibility: [reproduce](https://github.com/YunjueTech/Yunjue-Agent/tree/reproduce)
- For a detailed reproduction guide, please refer to that branch.
- **System Traces**: We provide full system traces on [Hugging Face](https://huggingface.co/datasets/YunjueTech/Yunjue-Agent-Traces) for analysis.

### 🎬 Demo Quick Start

> Note: Currently tested only on MacOS. If you encounter any issues, feel free to open an issue or submit a PR.

#### Web Demo

We provide a web demo that developers can deploy themselves to demonstrate Yunjue Agent's tool self-evolution capabilities and execution process. The first demo shows the Agent executing tool decomposition, creating tools to search and scrape PDFs from the internet; the second demo demonstrates the ability to search for US stock information by reusing existing tools.

```bash
source .venv/bin/activate
uvicorn web_demo.app:app --app-dir . --port 8000
```

- UI: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`
- Detailed guide: `docs/web_demo.md`

#### CLI Skill Demo

Yunjue Agent streamlines the path from expertise to action. By simply providing a `SKILL.md` as we believe high-level experience remains a human-driven asset, the agent autonomously generates the necessary tools to execute those skills. Experience the seamless transformation of documented knowledge into functional automation.

```bash
source .venv/bin/activate
python -m cli.cli
```

- Example skills: `example/cli/skills`
- Detailed guide: `docs/cli.md`

---

## 🤖 What is Yunjue Agent?

Conventional agent systems often struggle in open-ended environments where task distributions continuously drift and external supervision is scarce. Their reliance on static toolsets or offline training lags behind these dynamics, leaving the system's capability boundaries rigid and unknown. To address this, we propose the *In-Situ Self-Evolving* paradigm. This approach treats sequential task interactions as a continuous stream of experience, enabling the system to distill short-term execution feedback into long-term, reusable capabilities without access to ground-truth labels. Within this framework, we identify *tool evolution* as the critical pathway for capability expansion, which provides verifiable, binary feedback signals. Within this framework, we develop *Yunjue Agent*, a system that iteratively synthesizes, optimizes, and reuses tools to navigate emerging challenges. To optimize evolutionary efficiency, we further introduce a *Parallel Batch Evolution* strategy. Empirical evaluations across five diverse benchmarks under a zero-start setting demonstrate significant performance gains over proprietary baselines. Additionally, complementary warm-start evaluations confirm that the accumulated general knowledge can be seamlessly transferred to novel domains. Finally, we propose a novel metric to monitor evolution convergence, serving as a function analogous to training loss in conventional optimization. We open-source our codebase, system traces, and evolved tools to facilitate future research in resilient, self-evolving intelligence.

<img width="100%" alt="image" src="docs/assets/overview.jpeg" />

---

## 🌟 Highlights

- **🧬 In-situ Self-evolving Paradigm**
    
    We introduce a novel agentic learning framework that bridges the gap between static capability and on-the-fly evolving. By reframing discrete interactions as a continuous stream of experience, the system distills short-term inference into long-term capabilities via internal feedback loops. This enables real-time adaptation and exploration in open-ended environments without the need for additional supervision signals.
    
- **🚀 SOTA Performance from "Tabula Rasa"**
    
    Starting with an **empty tool library** (Zero-Start), our system achieves State-of-the-Art performance by relying solely on inference-time generation, verification, and induction. It demonstrates significant gains over backend models (e.g., **+17.4%** on DeepSearchQA over Gemini 3 Pro) and secures **2nd place on the HLE leaderboard**, proving the feasibility of bootstrapping general capabilities from scratch.
    
- **🛠️ "Tool-First" Evolutionary Principle**
    
    We prioritize tool evolution over Memory or Workflows as the primary driver of capability. Tools provide objective **Binary Feedback** (via code execution success/failure), serving as a reliable internal supervision signal in the absence of human annotation. This approach mitigates hallucination risks and prevents strategy bias, ensuring stable accumulation of general primitives.
    
- **🔍 Fully Reproducible & Open Traces**
    
    We release a comprehensive open-asset suite, including end-to-end code, benchmark scripts, versioned tool artifacts, and full interaction traces. This transforms "black-box" agent results into transparent, auditable research, enabling granular analysis of tool convergence, evolution efficiency, and merging strategies.

## 📈 Performance on Benchmarks

We benchmark Yunjue Agent on a series of benchmarks, including **HLE**, **DeepSearchQA**, **FinSearchComp (T2&T3)**, **xbench-ScienceQA** and **xbench-DeepSearch**, and achieved SOTA results.

<img width="100%" alt="image" src="docs/assets/main_results.jpeg" />



---

## 📚 Citation

If you find this work useful, please cite:

```bibtex
@misc{li2026yunjueagenttechreport,
      title={Yunjue Agent Tech Report: A Fully Reproducible, Zero-Start In-Situ Self-Evolving Agent System for Open-Ended Tasks}, 
      author={Haotian Li and Shijun Yang and Weizhen Qi and Silei Zhao and Rui Hua and Mingzhu Song and Xiaojian Yang and Chao Peng},
      year={2026},
      eprint={2601.18226},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2601.18226}, 
}
```

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=YunjueTech/Yunjue-Agent&type=date&legend=top-left)](https://www.star-history.com/#YunjueTech/Yunjue-Agent&type=date&legend=top-left)

---


## 📄 License

This project is licensed under the Apache License 2.0.
