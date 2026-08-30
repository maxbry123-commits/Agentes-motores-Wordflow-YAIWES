"""Run the synthetic calibration example without installing dependencies."""

from pathlib import Path

from ai4s_agent_lab.toy_decay import run_demo


if __name__ == "__main__":
    result = run_demo(Path("artifacts/decay_demo"), iterations=6)
    print(f"best decay rate: {result.best_proposal.parameters['decay_rate']:.4f}")
    print(f"best RMSE: {result.best_result.metrics['rmse']:.6f}")
