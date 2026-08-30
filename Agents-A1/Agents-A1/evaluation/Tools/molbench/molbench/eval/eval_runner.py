# Evaluation logic: one dataset maps to one class; run_agent imports and calls the matching class when dataset==x and task==y.
# Note: we ALSO write back per-sample metrics into each preds/*.json entry under key "metrics" (idempotent overwrite),
# while keeping the official aggregate scoring logic unchanged.
#
# ChemCoTBench (mol_edit, mol_und, mol_opt): we chdir to eval_root (baseline_and_eval) before calling official eval,
# so cwd matches the official notebook and TDC oracle uses ./oracle = baseline_and_eval/oracle. Reaction eval uses
# only rdkit (no official eval module), so no chdir.
from __future__ import annotations

import json
import os
import shutil
import sys
import importlib.util
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence


def _ensure_eval_path(eval_root: str) -> None:
    """Insert official baseline_and_eval as sys.path[0] so 'from eval.eval_metric' resolves to baseline_and_eval/eval/."""
    if not eval_root:
        return
    abs_root = os.path.abspath(eval_root)
    if abs_root in sys.path:
        # move to front so official eval wins over project's eval package
        sys.path.remove(abs_root)
    sys.path.insert(0, abs_root)
    eval_dir = os.path.join(abs_root, "eval")
    if os.path.isdir(eval_dir):
        import types

        mod = sys.modules.get("eval")
        if mod is None or not hasattr(mod, "__path__"):
            mod = types.ModuleType("eval")
            mod.__path__ = [eval_dir]  # type: ignore[attr-defined]
            sys.modules["eval"] = mod
        elif eval_dir not in list(getattr(mod, "__path__", [])):
            mod.__path__.insert(0, eval_dir)  # type: ignore[attr-defined]


def _load_official_eval_module(eval_root: str, module_name: str):
    """Load official eval module from baseline_and_eval/eval/<module_name>.py."""
    path = os.path.join(os.path.abspath(eval_root), "eval", f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(f"official_{module_name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ensure_oracle_compat_files(eval_root: str) -> None:
    """Validate external ChemCoTBench oracle artifacts and expose compatibility names."""
    oracle_dir = os.path.join(os.path.abspath(eval_root), "oracle")
    required = ("drd2_current.pkl", "gsk3b_current.pkl", "jnk3_current.pkl", "fpscores.pkl")
    if not os.path.isdir(oracle_dir):
        raise FileNotFoundError(
            "ChemCoTBench oracle artifacts are not bundled in this code-only release. "
            f"Restore them under {oracle_dir} before running oracle-based evaluation."
        )
    missing = [name for name in required if not os.path.exists(os.path.join(oracle_dir, name))]
    if missing:
        raise FileNotFoundError(
            "Missing ChemCoTBench oracle artifact(s): " + ", ".join(missing) +
            f". Restore the external oracle bundle under {oracle_dir}."
        )
    for expected, cached in (
        ("gsk3b.pkl", "gsk3b_current.pkl"),
        ("jnk3.pkl", "jnk3_current.pkl"),
    ):
        expected_path = os.path.join(oracle_dir, expected)
        cached_path = os.path.join(oracle_dir, cached)
        if os.path.exists(expected_path):
            continue
        try:
            os.symlink(cached, expected_path)
        except Exception:
            shutil.copyfile(cached_path, expected_path)


def _ensure_tdc_compat() -> None:
    """Provide the subset of tdc.Oracle needed by physchem eval when PyTDC is absent."""
    try:
        import tdc  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    import types
    from rdkit import Chem
    from rdkit.Chem import Crippen, Descriptors

    class Oracle:
        def __init__(self, name: str) -> None:
            self.name = str(name or "").lower()
            supported = {"logp", "qed"}
            if self.name not in supported:
                raise ModuleNotFoundError(
                    "No module named 'tdc'; lightweight MolClaw fallback only supports "
                    f"{sorted(supported)}, got {self.name!r}"
                )

        def __call__(self, smiles: str) -> float:
            mol = Chem.MolFromSmiles(str(smiles or ""))
            if mol is None:
                return 0.0
            if self.name == "logp":
                return float(Crippen.MolLogP(mol))
            if self.name == "qed":
                return float(Descriptors.qed(mol))
            return 0.0

    mod = types.ModuleType("tdc")
    mod.Oracle = Oracle  # type: ignore[attr-defined]
    sys.modules["tdc"] = mod


def _ensure_rdkit_six_compat() -> None:
    """Provide compatibility modules used by ChemCoTBench/TDC legacy pickles."""
    if "rdkit.six" in sys.modules:
        rdkit_six_ready = True
    else:
        rdkit_six_ready = False

    import importlib
    import types

    if not rdkit_six_ready:
        mod = types.ModuleType("rdkit.six")

        def iteritems(mapping):
            return mapping.items()

        mod.iteritems = iteritems  # type: ignore[attr-defined]
        sys.modules["rdkit.six"] = mod

    legacy_modules = {
        "sklearn.svm.classes": "sklearn.svm._classes",
        "sklearn.ensemble.forest": "sklearn.ensemble._forest",
        "sklearn.tree.tree": "sklearn.tree._classes",
    }
    for old_name, new_name in legacy_modules.items():
        if old_name not in sys.modules:
            try:
                sys.modules[old_name] = importlib.import_module(new_name)
            except Exception:
                pass

    try:
        import numpy as np
        from sklearn.tree import _tree

        if not getattr(_tree._check_node_ndarray, "_molclaw_compat", False):
            original_check_node_ndarray = _tree._check_node_ndarray

            def check_node_ndarray_compat(node_ndarray, expected_dtype):
                names = getattr(node_ndarray.dtype, "names", None) or ()
                expected_names = getattr(expected_dtype, "names", None) or ()
                if "missing_go_to_left" in expected_names and "missing_go_to_left" not in names:
                    converted = np.zeros(node_ndarray.shape, dtype=expected_dtype)
                    for name in names:
                        converted[name] = node_ndarray[name]
                    return original_check_node_ndarray(converted, expected_dtype)
                return original_check_node_ndarray(node_ndarray, expected_dtype)

            check_node_ndarray_compat._molclaw_compat = True  # type: ignore[attr-defined]
            _tree._check_node_ndarray = check_node_ndarray_compat
    except Exception:
        pass

    try:
        from tdc.chem_utils.oracle import oracle as tdc_oracle

        if not hasattr(tdc_oracle, "_molclaw_original_jnk3"):
            tdc_oracle._molclaw_original_jnk3 = tdc_oracle.jnk3
        original_jnk3_cls = tdc_oracle._molclaw_original_jnk3

        def drd2_compat(smile):
            if "drd2_model" not in vars(tdc_oracle):
                tdc_oracle.drd2_model = tdc_oracle.load_drd2_model()
            mol = tdc_oracle.Chem.MolFromSmiles(smile)
            if not mol:
                return 0.0
            fp = tdc_oracle.fingerprints_from_mol(mol)
            score = tdc_oracle.drd2_model.predict_proba(fp)[:, 1]
            try:
                return float(score)
            except TypeError:
                return float(score[0])

        def _repair_forest_model(model):
            if not hasattr(model, "estimator") and getattr(model, "estimators_", None):
                model.estimator = model.estimators_[0]
            if hasattr(model, "estimator") and not hasattr(model.estimator, "monotonic_cst"):
                model.estimator.monotonic_cst = None
            for estimator in getattr(model, "estimators_", []) or []:
                if not hasattr(estimator, "monotonic_cst"):
                    estimator.monotonic_cst = None
            return model

        def gsk3b_compat(smiles):
            if "gsk3_model" not in vars(tdc_oracle):
                tdc_oracle.gsk3_model = _repair_forest_model(tdc_oracle.load_gsk3b_model())
            molecule = tdc_oracle.smiles_to_rdkit_mol(smiles)
            fp = tdc_oracle.AllChem.GetMorganFingerprintAsBitVect(molecule, 2, nBits=2048)
            features = tdc_oracle.np.zeros((1,))
            tdc_oracle.DataStructs.ConvertToNumpyArray(fp, features)
            fp = features.reshape(1, -1)
            return float(tdc_oracle.gsk3_model.predict_proba(fp)[0, 1])

        class jnk3_compat:
            def __init__(self):
                self.jnk3_model = _repair_forest_model(original_jnk3_cls().jnk3_model)

            def __call__(self, smiles):
                molecule = tdc_oracle.smiles_to_rdkit_mol(smiles)
                fp = tdc_oracle.AllChem.GetMorganFingerprintAsBitVect(molecule, 2, nBits=2048)
                features = tdc_oracle.np.zeros((1,))
                tdc_oracle.DataStructs.ConvertToNumpyArray(fp, features)
                fp = features.reshape(1, -1)
                return float(self.jnk3_model.predict_proba(fp)[0, 1])

        tdc_oracle.drd2 = drd2_compat
        tdc_oracle.gsk3b = gsk3b_compat
        tdc_oracle.jnk3 = jnk3_compat
        try:
            import tdc.chem_utils as tdc_chem_utils

            tdc_chem_utils.drd2 = drd2_compat
            tdc_chem_utils.gsk3b = gsk3b_compat
            tdc_chem_utils.jnk3 = jnk3_compat
        except Exception:
            pass
    except Exception:
        pass

def _write_json_overwrite(path: str, obj: Any) -> None:
    """Overwrite JSON file with stable formatting."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _ensure_smiles_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if v is not None and str(v).strip()]
    if isinstance(value, str):
        payload = value.strip()
        if not payload:
            return []
        try:
            parsed = json.loads(payload)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed if v is not None and str(v).strip()]
        except json.JSONDecodeError:
            pass
        return [payload]
    return []


def _extract_candidates_from_user_query(entry: Dict[str, Any]) -> List[str]:
    raw = entry.get("user_query")
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, dict):
        return []
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        return []
    return [str(v).strip() for v in candidates if v is not None and str(v).strip()]


def _get_candidates_for_entry(entry: Dict[str, Any]) -> List[str]:
    candidates = _ensure_smiles_list(entry.get("candidates"))
    if candidates:
        return candidates
    return _extract_candidates_from_user_query(entry)


def _get_predicted_ranking(raw_results: Any) -> List[str]:
    """Return model predicted full ranking when available, otherwise fallback to top3 list."""
    if isinstance(raw_results, str):
        try:
            raw_results = json.loads(raw_results)
        except json.JSONDecodeError:
            return []

    if isinstance(raw_results, list):
        return _ensure_smiles_list(raw_results)

    if not isinstance(raw_results, dict):
        return []

    for key in ("ranking", "ranked", "ordered", "predicted_ranking", "top3"):
        values = _ensure_smiles_list(raw_results.get(key))
        if values:
            return values
    return []


def _build_rank_map(candidates: Sequence[str]) -> Dict[str, int]:
    return {candidate: idx + 1 for idx, candidate in enumerate(candidates)}


def _best_candidate_rank(top3: Sequence[str], rank_map: Dict[str, int], fallback: int) -> int:
    best: int | None = None
    for cand in top3:
        actual = rank_map.get(cand)
        if actual is None:
            continue
        if best is None or actual < best:
            best = actual
    if best is not None:
        return best
    return fallback


def _compute_molbench_vs_metrics(entry: Dict[str, Any]) -> Dict[str, float]:
    answers = _ensure_smiles_list(entry.get("answer"))
    gt_top3 = answers[:3]
    candidates = _get_candidates_for_entry(entry)
    raw_results = entry.get("json_results") or {}
    predicted_ranking = _get_predicted_ranking(raw_results)
    predicted_rank_map = _build_rank_map(predicted_ranking)

    top3_candidates = predicted_ranking[:3]
    gt_set = {cand for cand in answers}

    hit_positions: List[int] = []
    for pos, candidate in enumerate(top3_candidates, start=1):
        if candidate in gt_set:
            hit_positions.append(pos)

    hit_at_3 = 1.0 if hit_positions else 0.0
    hit_count = len(hit_positions)
    top3_hit_rate = hit_count / 3.0

    fallback_rank = (len(candidates) + 1) if candidates else 61
    gt_ranks = [float(predicted_rank_map.get(gt, fallback_rank)) for gt in gt_top3]
    avg_rank = float(sum(gt_ranks) / len(gt_ranks)) if gt_ranks else float(fallback_rank)

    return {
        "hit_at_3": float(hit_at_3),
        "hit_num": float(hit_count),
        # Keep field name "rank" for backward compatibility; semantic is GT-top3 average rank.
        "rank": avg_rank,
        "gt_top3_avg_rank": avg_rank,
        "gt_top3_count": float(len(gt_top3)),
        "top3_hit_rate": float(top3_hit_rate),
    }


class BaseEval(ABC):
    """Base evaluation class: one dataset (or dataset+sub_dataset) maps to one subclass."""
    dataset: str = ""
    sub_dataset: str = ""

    @abstractmethod
    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        """Read pred JSON from preds_dir, run evaluation, return score dict."""
        pass


# ---------- ChemCoTBench mol_edit ----------
class ChemCoTBenchMolEditEval(BaseEval):
    dataset = "ChemCoTBench"
    sub_dataset = "molbench-mo-edit"

    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        _ensure_eval_path(eval_root)
        mod = _load_official_eval_module(eval_root, "eval_moledit")
        eval_moledit_from_list = mod.eval_moledit_from_list
        tf = getattr(mod, "tranform_str_to_json", lambda x: json.loads(x) if x else None)
        check_edit_add_valid = getattr(mod, "check_edit_add_valid", None)
        check_edit_del_valid = getattr(mod, "check_edit_del_valid", None)
        check_edit_sub_valid = getattr(mod, "check_edit_sub_valid", None)
        out = {}
        preds_dir = os.path.abspath(preds_dir)
        if not os.path.isdir(preds_dir):
            return out
        eval_root_abs = os.path.abspath(eval_root)
        saved_cwd = os.getcwd()
        score_prefix = self.sub_dataset
        try:
            os.chdir(eval_root_abs)
            for fn in sorted(os.listdir(preds_dir)):
                if not fn.endswith(".json"):
                    continue
                subtask = os.path.splitext(fn)[0]
                path = os.path.join(preds_dir, fn)
                with open(path, "r", encoding="utf-8") as f:
                    pred_list = json.load(f)
                if not isinstance(pred_list, list):
                    continue
                src_list, pred_smi, group_a, group_b = [], [], [], []
                # Write back per-sample metrics (matches official: missing/invalid extraction contributes 0 in denominators)
                for p in pred_list:
                    jr = p.get("json_results")
                    if isinstance(jr, str):
                        jr = tf(jr) if callable(tf) else json.loads(jr) if jr else None
                    smi = (jr or {}).get("output")
                    extracted = 1 if (smi is not None and str(smi).strip() != "") else 0
                    is_correct = 0
                    if extracted:
                        try:
                            if subtask == "add" and callable(check_edit_add_valid):
                                is_correct = 1 if check_edit_add_valid(src=p.get("molecule", ""), tgt=smi, group=p.get("added_group")) else 0
                            elif subtask == "delete" and callable(check_edit_del_valid):
                                is_correct = 1 if check_edit_del_valid(src=p.get("molecule", ""), tgt=smi, group=p.get("removed_group")) else 0
                            elif subtask == "sub" and callable(check_edit_sub_valid):
                                is_correct = 1 if check_edit_sub_valid(
                                    src=p.get("molecule", ""),
                                    tgt=smi,
                                    remove_group=p.get("removed_group"),
                                    add_group=p.get("added_group"),
                                ) else 0
                        except Exception:
                            is_correct = 0
                    # Use keys aligned with official aggregate dict so per-sample mean matches aggregates.
                    p["metrics"] = {
                        "correct_rate": float(is_correct),
                        f"{subtask}-valid-rate": float(extracted),
                    }
                for p in pred_list:
                    jr = p.get("json_results")
                    if isinstance(jr, str):
                        jr = tf(jr) if callable(tf) else json.loads(jr) if jr else None
                    if jr and "output" in jr:
                        pred_smi.append(jr["output"])
                        src_list.append(p["molecule"])
                        if subtask == "add":
                            group_a.append(p.get("added_group"))
                        elif subtask == "delete":
                            group_a.append(p.get("removed_group"))
                        else:
                            group_a.append(p.get("added_group"))
                            group_b.append(p.get("removed_group"))
                if pred_smi:
                    score = eval_moledit_from_list(
                        src_list=src_list, pred_list=pred_smi, group_a=group_a, group_b=group_b,
                        task=subtask, total_number=len(pred_list)
                    )
                    if isinstance(score, dict):
                        score = dict(score)
                        score["n_samples"] = len(pred_list)
                    out[f"{score_prefix}_{subtask}"] = score
                else:
                    # No parseable outputs extracted for this subtask: report deterministic zero score.
                    out[f"{score_prefix}_{subtask}"] = {
                        "correct_rate": 0.0,
                        f"{subtask}-valid-rate": 0.0,
                        "n_samples": len(pred_list),
                    }
                # Persist per-sample metrics back into preds file (overwrite)
                _write_json_overwrite(path, pred_list)
        finally:
            os.chdir(saved_cwd)
        return out



# ---------- ChemCoTBench mol_opt ----------
def _run_chemcot_mol_opt_eval(preds_dir: str, eval_root: str, score_prefix: str) -> Dict[str, Any]:
    _ensure_oracle_compat_files(eval_root)
    _ensure_tdc_compat()
    _ensure_rdkit_six_compat()
    _ensure_eval_path(eval_root)
    mod = _load_official_eval_module(eval_root, "eval_molopt")
    eval_molopt_from_list = mod.eval_molopt_from_list
    tf = getattr(mod, "tranform_str_to_json", lambda x: json.loads(x) if x else None)
    metric_mod = _load_official_eval_module(eval_root, "eval_metric")
    mol_opt_evaluater = getattr(metric_mod, "mol_opt_evaluater", None)
    is_valid_smiles = getattr(metric_mod, "is_valid_smiles", None)
    out: Dict[str, Any] = {}
    preds_dir = os.path.abspath(preds_dir)
    if not os.path.isdir(preds_dir):
        return out
    # TDC loads oracle from cwd: ./oracle/*.pkl; match official by running from eval_root (baseline_and_eval)
    eval_root_abs = os.path.abspath(eval_root)
    saved_cwd = os.getcwd()
    try:
        os.chdir(eval_root_abs)
        for fn in sorted(os.listdir(preds_dir)):
            if not fn.endswith(".json"):
                continue
            subtask = os.path.splitext(fn)[0]
            path = os.path.join(preds_dir, fn)
            with open(path, "r", encoding="utf-8") as f:
                pred_list = json.load(f)
            if not isinstance(pred_list, list):
                continue
            tgt_list, src_list = [], []
            # Per-sample metrics: improvement delta + scaffold (hard/soft). Missing extraction => delta=0, scaffold=0.
            prop_dict = dict(logp="logp", solubility="solubility", qed="qed", drd="drd2", jnk="jnk3", gsk="gsk3b")
            prop_name = prop_dict.get(subtask)
            oracle_error = ""
            try:
                evaluator = mol_opt_evaluater(prop=prop_name) if (prop_name and callable(mol_opt_evaluater)) else None
            except Exception as e:
                evaluator = None
                oracle_error = f"{type(e).__name__}: {e}"
            for p in pred_list:
                jr = p.get("json_results")
                if isinstance(jr, str):
                    jr = tf(jr)
                smi = (jr or {}).get("Final Target Molecule") or (jr or {}).get("Final_Target_Molecule")
                src = p.get("src_smiles", "")
                extracted = 1 if (smi is not None and str(smi).strip() != "") else 0
                delta = 0.0
                valid_pair = 0
                valid_score = 0
                scaffold_hard = 0.0
                scaffold_soft = 0.0
                if extracted and evaluator is not None and callable(is_valid_smiles):
                    try:
                        if is_valid_smiles(str(src)) and is_valid_smiles(str(smi)):
                            valid_pair = 1
                            s_src = evaluator.property_oracle(src)
                            s_tgt = evaluator.property_oracle(smi)
                            if s_src is not None and s_tgt is not None:
                                valid_score = 1
                                delta = float(s_tgt) - float(s_src)
                            # scaffold_consistency is robust to invalid/empty; but we already checked validity here
                            h, soft_sum = evaluator.scaffold_consistency([src], [smi])
                            scaffold_hard = float(h)  # count_same for single sample (0/1)
                            scaffold_soft = float(soft_sum)  # similarity for single sample (0~1)
                    except Exception:
                        delta = 0.0
                        valid_pair = 0
                        valid_score = 0
                        scaffold_hard = 0.0
                        scaffold_soft = 0.0
                p["metrics"] = {
                    "improvement": float(delta),
                    "valid_smiles_pair": float(valid_pair),
                    "valid_score_pair": float(valid_score),
                    "scaffold_hard": float(scaffold_hard),
                    "scaffold_soft": float(scaffold_soft),
                    "valid_smiles_extract": float(extracted),
                }
                if jr and smi:
                    tgt_list.append(smi)
                    src_list.append(p["src_smiles"])
            if oracle_error:
                score = {
                    "oracle_available": False,
                    "error": oracle_error,
                    "n_samples": len(pred_list),
                }
            else:
                try:
                    score = eval_molopt_from_list(
                        optimized_prop=subtask, gt_list=src_list, pred_list=tgt_list, total_number=len(pred_list)
                    )
                except Exception as e:
                    score = {
                        "oracle_available": False,
                        "error": f"{type(e).__name__}: {e}",
                        "n_samples": len(pred_list),
                    }
            if isinstance(score, dict):
                score = dict(score)
                score["n_samples"] = len(pred_list)
            out[f"{score_prefix}_{subtask}"] = score
            _write_json_overwrite(path, pred_list)
    finally:
        os.chdir(saved_cwd)
    return out


class ChemCoTBenchMolOptPhyschemEval(BaseEval):
    dataset = "ChemCoTBench"
    sub_dataset = "molbench-mo-opt"

    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        return _run_chemcot_mol_opt_eval(preds_dir, eval_root, self.sub_dataset)


class ChemCoTBenchMolOptTargetEval(BaseEval):
    dataset = "ChemCoTBench"
    sub_dataset = "mol_opt_target"

    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        return _run_chemcot_mol_opt_eval(preds_dir, eval_root, self.sub_dataset)


class ChemCoTBenchMolOptEval(BaseEval):
    dataset = "ChemCoTBench"
    sub_dataset = "mol_opt"

    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        return _run_chemcot_mol_opt_eval(preds_dir, eval_root, self.sub_dataset)



# ---------- ChemCoTBench mol_und (strictly follow official eval.eval_molund, no extra scaling) ----------
class ChemCoTBenchMolUndEval(BaseEval):
    dataset = "ChemCoTBench"
    sub_dataset = "mol_und"

    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        _ensure_oracle_compat_files(eval_root)
        _ensure_tdc_compat()
        _ensure_rdkit_six_compat()
        _ensure_eval_path(eval_root)
        mod = _load_official_eval_module(eval_root, "eval_molund")
        eval_molund_from_list = mod.eval_molund_from_list
        tf = getattr(mod, "tranform_str_to_json", lambda x: json.loads(x) if x else None)
        metric_mod = _load_official_eval_module(eval_root, "eval_metric")
        mol_opt_evaluater = getattr(metric_mod, "mol_opt_evaluater", None)
        out = {}
        preds_dir = os.path.abspath(preds_dir)
        if not os.path.isdir(preds_dir):
            return out
        eval_root_abs = os.path.abspath(eval_root)
        saved_cwd = os.getcwd()
        score_prefix = self.sub_dataset
        try:
            os.chdir(eval_root_abs)
            for fn in sorted(os.listdir(preds_dir)):
                if not fn.endswith(".json"):
                    continue
                subtask = os.path.splitext(fn)[0]
                path = os.path.join(preds_dir, fn)
                with open(path, "r", encoding="utf-8") as f:
                    pred_list = json.load(f)
                if not isinstance(pred_list, list):
                    continue
                gt_list = []
                pred_values = []
                # For Murcko_scaffold: use official scaffold_consistency (per-sample similarity) via mol_opt_evaluater(prop='qed')
                scaffold_eval = mol_opt_evaluater(prop="qed") if (subtask in ("murcko", "Murcko_scaffold") and callable(mol_opt_evaluater)) else None
                for p in pred_list:
                    gt_list.append(p.get("gt"))
                    jr = p.get("json_results")
                    if isinstance(jr, str):
                        jr = tf(jr) if callable(tf) else json.loads(jr) if jr else None
                    if subtask in ("equivalence", "ring_system_scaffold"):
                        v = (jr or {}).get("output")
                        pred_values.append(v if v is not None else "")
                    elif subtask in ("ring_count", "fg_count"):
                        v = (jr or {}).get("count")
                        pred_values.append(int(v) if v is not None else 0)
                    elif subtask == "Murcko_scaffold":
                        v = (jr or {}).get("Output Scaffold")
                        pred_values.append(v if v is not None else "")
                    else:
                        pred_values.append((jr or {}).get("output", ""))
                if not pred_list:
                    continue
                total_number = len(pred_list)
                # null/invalid = extraction failure, treated as failure case, not filtered; official scaffold_consistency needs to handle null/invalid (score 0 without crashing)
                score = eval_molund_from_list(
                    gt_list=gt_list, pred_list=pred_values, total_number=total_number, task=subtask
                )
                if isinstance(score, dict):
                    score = dict(score)
                    score["n_samples"] = total_number
                    # Official eval_molund does not set score for equivalence when len(pred_list)>0; set it per formula
                    if subtask == "equivalence" and score.get("score") is None and pred_values:
                        count = sum(
                            1 for i in range(len(pred_values))
                            if str(pred_values[i] or "").strip().lower() == str(gt_list[i] or "").strip().lower()
                        )
                        score["score"] = count / len(pred_values)
                out[f"{score_prefix}_{subtask}"] = score
                # Write per-sample metrics back (align with official "score" semantics for each subtask)
                for i in range(total_number):
                    per_score = 0.0
                    try:
                        if subtask in ("ring_system", "ring_system_scaffold", "permutated"):
                            per_score = 1.0 if str(pred_values[i] or "").strip().lower() == "yes" else 0.0
                        elif subtask == "mutated":
                            per_score = 1.0 if str(pred_values[i] or "").strip().lower() == "no" else 0.0
                        elif subtask == "equivalence":
                            per_score = 1.0 if str(pred_values[i] or "").strip().lower() == str(gt_list[i] or "").strip().lower() else 0.0
                        elif subtask in ("ring_count", "fg_samples", "fg_count"):
                            per_score = float(abs(int(pred_values[i]) - int(gt_list[i] or 0)))
                        elif subtask in ("murcko", "Murcko_scaffold") and scaffold_eval is not None:
                            # similarity in [0,1]; invalid/empty handled in official scaffold_consistency (returns 0)
                            _, soft_sum = scaffold_eval.scaffold_consistency([gt_list[i] or ""], [pred_values[i] or ""])
                            per_score = float(soft_sum)
                        else:
                            # Default: treat as exact-match to gt if possible
                            per_score = 1.0 if str(pred_values[i] or "").strip().lower() == str(gt_list[i] or "").strip().lower() else 0.0
                    except Exception:
                        per_score = 0.0
                    pred_list[i]["metrics"] = {"score": float(per_score)}
                _write_json_overwrite(path, pred_list)
        finally:
            os.chdir(saved_cwd)
        return out



# ---------- ChemCoTBench reaction: official keys per subtask (fs=Major Product+Byproduct(s), retro=Reactants, rcr=SMILES, nepp=pred_smi, mechsel=choice) ----------
def _reaction_gt_to_smiles_str(gt: Any, subtask: str) -> str:
    """Normalize gt to string for SMILES-based comparison. Official format: fs=JSON with Major Product/Byproduct(s); retro/rcr/nepp=plain string."""
    if gt is None:
        return ""
    s = gt if isinstance(gt, str) else str(gt)
    s = (s or "").strip()
    if subtask == "fs" and s.startswith("{"):
        try:
            d = json.loads(s)
            if isinstance(d, dict) and "Major Product" in d and d["Major Product"] is not None:
                return str(d["Major Product"]).strip()
        except (json.JSONDecodeError, TypeError):
            pass
    return s


class ChemCoTBenchReactionEval(BaseEval):
    """Reaction eval strictly following ChemCoTBench baseline_and_eval: top_1, fts, acc only."""

    dataset = "ChemCoTBench"
    sub_dataset = "reaction"

    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        # Replicate official evaluator.py + rxn_eval_demo.ipynb: canonical SMILES, exact_match (InChI), rdk/maccs/morgan, validity; report top_1, fts, acc only.
        from rdkit import Chem
        from rdkit.Chem import MACCSkeys, AllChem
        from rdkit import DataStructs

        def convert_to_canonical_smiles(smiles: str):
            if not smiles or not isinstance(smiles, str):
                return None
            try:
                mol = Chem.MolFromSmiles(smiles.strip())
                return Chem.MolToSmiles(mol, isomericSmiles=False, canonical=True) if mol else None
            except Exception:
                return None

        def exact_match(ot_smi, gt_smi):
            try:
                m_out = Chem.MolFromSmiles(ot_smi)
                m_gt = Chem.MolFromSmiles(gt_smi)
                if m_out and m_gt and Chem.MolToInchi(m_out) == Chem.MolToInchi(m_gt):
                    return 1
            except Exception:
                pass
            return 0

        def rdk_similarity(ot_m, gt_m):
            return DataStructs.FingerprintSimilarity(
                Chem.RDKFingerprint(gt_m), Chem.RDKFingerprint(ot_m), metric=DataStructs.TanimotoSimilarity
            )

        def maccs_similarity(ot_m, gt_m):
            return DataStructs.FingerprintSimilarity(
                MACCSkeys.GenMACCSKeys(gt_m), MACCSkeys.GenMACCSKeys(ot_m), metric=DataStructs.TanimotoSimilarity
            )

        def morgan_similarity(ot_m, gt_m, radius=2):
            return DataStructs.TanimotoSimilarity(
                AllChem.GetMorganFingerprint(gt_m, radius), AllChem.GetMorganFingerprint(ot_m, radius)
            )

        out: Dict[str, Any] = {}
        score_prefix = self.sub_dataset
        if not os.path.isdir(preds_dir):
            return out
        for fn in sorted(os.listdir(preds_dir)):
            if not fn.endswith(".json"):
                continue
            subtask = os.path.splitext(fn)[0]
            path = os.path.join(preds_dir, fn)
            with open(path, "r", encoding="utf-8") as f:
                pred_list = json.load(f)
            if not isinstance(pred_list, list):
                continue
            if not pred_list:
                continue
            n = len(pred_list)

            if subtask == "mechsel":
                # Official rxn_eval_demo: MCQ Accuracy only → report acc
                pred_choices = []
                gt_choices = []
                for p in pred_list:
                    gt_choices.append((p.get("gt") or "").strip().upper()[:1])
                    jr = p.get("json_results")
                    if isinstance(jr, str):
                        try:
                            jr = json.loads(jr)
                        except Exception:
                            jr = None
                    pred_choices.append((jr or {}).get("choice") or "")
                acc = sum(1 for i in range(n) if pred_choices[i] == gt_choices[i]) / n if n else 0.0
                for i in range(n):
                    pred_list[i]["metrics"] = {"acc": float(1.0 if pred_choices[i] == gt_choices[i] else 0.0)}
                _write_json_overwrite(path, pred_list)
                out[f"{score_prefix}_{subtask}"] = {"acc": acc, "n_samples": n}
                continue

            # SMILES subtasks (fs, retro, rcr, nepp): official MoleculeSMILESEvaluator then top_1, fts
            pred_strs = []
            gt_strs = []
            for p in pred_list:
                gt_strs.append(_reaction_gt_to_smiles_str(p.get("gt"), subtask))
                jr = p.get("json_results")
                if isinstance(jr, str):
                    try:
                        jr = json.loads(jr)
                    except Exception:
                        jr = None
                pred_strs.append((jr or {}).get("SMILES") or "")
            exact_list, rdk_list, maccs_list, morgan_list, valid_list = [], [], [], [], []
            for i in range(n):
                pred_canon = convert_to_canonical_smiles(pred_strs[i])
                gt_canon = convert_to_canonical_smiles(gt_strs[i])
                valid_list.append(1 if pred_canon is not None else 0)
                if pred_canon is None or gt_canon is None:
                    exact_list.append(0)
                    rdk_list.append(0)
                    maccs_list.append(0)
                    morgan_list.append(0)
                    pred_list[i]["metrics"] = {
                        "top_1": 0.0,
                        "validity": float(valid_list[-1]),
                        "rdk": 0.0,
                        "maccs": 0.0,
                        "morgan": 0.0,
                        "fts": 0.0,
                    }
                    continue
                exact_list.append(exact_match(pred_canon, gt_canon))
                try:
                    m_p = Chem.MolFromSmiles(pred_canon)
                    m_g = Chem.MolFromSmiles(gt_canon)
                    if m_p and m_g:
                        rdk_list.append(rdk_similarity(m_p, m_g))
                        maccs_list.append(maccs_similarity(m_p, m_g))
                        morgan_list.append(morgan_similarity(m_p, m_g))
                    else:
                        rdk_list.append(0)
                        maccs_list.append(0)
                        morgan_list.append(0)
                except Exception:
                    rdk_list.append(0)
                    maccs_list.append(0)
                    morgan_list.append(0)
                # per-sample fts = (rdk + maccs + morgan)/3 * validity
                v = float(valid_list[-1])
                fts_i = ((float(rdk_list[-1]) + float(maccs_list[-1]) + float(morgan_list[-1])) / 3.0) * v
                pred_list[i]["metrics"] = {
                    "top_1": float(exact_list[-1]),
                    "validity": v,
                    "rdk": float(rdk_list[-1]),
                    "maccs": float(maccs_list[-1]),
                    "morgan": float(morgan_list[-1]),
                    "fts": float(fts_i),
                }
            if not exact_list:
                continue
            mean_exact = sum(exact_list) / len(exact_list)
            mean_rdk = sum(rdk_list) / len(rdk_list)
            mean_maccs = sum(maccs_list) / len(maccs_list)
            mean_morgan = sum(morgan_list) / len(morgan_list)
            mean_valid = sum(valid_list) / len(valid_list)
            # Official rxn_eval_demo: fts = (rdk_sims + maccs_sims + morgan_sims) / 3 * validity
            fts = (mean_rdk + mean_maccs + mean_morgan) / 3.0 * mean_valid
            _write_json_overwrite(path, pred_list)
            out[f"{score_prefix}_{subtask}"] = {"top_1": mean_exact, "fts": round(fts, 4), "n_samples": n}
        return out



# ---------- ACNet_curated QA (exact match) ----------


class ACNetCuratedEval(BaseEval):
    """Exact match evaluation for ACNet_curated QA bench.

    Each preds file under preds/acnet_curated/*.json is a list of entries with:
      - gt: ground-truth answer string
      - json_results.output: model output string (from <answer>...</answer>)
    Metric:
      - acc: mean exact match rate
    Also writes back per-sample metrics under entry["metrics"] = {"score": 0.0/1.0}.
    """

    dataset = "molbench-ms-2"
    sub_dataset = "acnet_curated"

    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        preds_dir = os.path.abspath(preds_dir)
        if not os.path.isdir(preds_dir):
            return out
        for fn in sorted(os.listdir(preds_dir)):
            if not fn.endswith(".json"):
                continue
            subtask = os.path.splitext(fn)[0]
            path = os.path.join(preds_dir, fn)
            with open(path, "r", encoding="utf-8") as f:
                pred_list = json.load(f)
            if not isinstance(pred_list, list) or not pred_list:
                continue
            scores: List[int] = []
            valid_flags: List[int] = []
            for p in pred_list:
                gt = p.get("gt") or ""
                jr = p.get("json_results") if isinstance(p, dict) else None
                pred = ""
                if isinstance(jr, dict):
                    pred = jr.get("output") or ""
                # 预测是否等于候选中的任意一个（至少选对对象）
                s1 = p.get("s1") or ""
                s2 = p.get("s2") or ""
                is_valid_choice = 1 if pred in (s1, s2) else 0
                is_correct = 1 if pred == gt else 0
                scores.append(is_correct)
                valid_flags.append(is_valid_choice)
                if isinstance(p, dict):
                    p["metrics"] = {
                        "score": float(is_correct),
                        "valid_choice": float(is_valid_choice),
                    }
            n = len(pred_list)
            acc = (sum(scores) / n) if scores else 0.0
            valid_rate = (sum(valid_flags) / n) if valid_flags else 0.0
            out[f"acnet_curated_{subtask}"] = {
                "acc": acc,
                "valid_rate": valid_rate,
                "n_samples": n,
            }
            _write_json_overwrite(path, pred_list)
        return out


# ---------- Virtual_Screening_curated (Top-3 hit rate) ----------


class VirtualScreeningCuratedEval(BaseEval):
    """Top-3 hit-rate evaluation for Virtual_Screening_curated bench.

    Each preds file under preds/virtual_screening_curated/*.json is a list of entries with:
      - answer: ground-truth SMILES list (subset of 60 candidates)
      - json_results.top3: model-predicted Top-3 SMILES list

    Metric:
      - hit_at_3: mean indicator of (pred ∩ answer != ∅)
    Also writes back per-sample metrics under entry["metrics"] = {"hit_at_3": 0.0/1.0}.
    """

    dataset = "Virtual_Screening_curated"
    sub_dataset = "virtual_screening_curated"

    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        preds_dir = os.path.abspath(preds_dir)
        if not os.path.isdir(preds_dir):
            return out
        for fn in sorted(os.listdir(preds_dir)):
            if not fn.endswith(".json"):
                continue
            subtask = os.path.splitext(fn)[0]
            path = os.path.join(preds_dir, fn)
            with open(path, "r", encoding="utf-8") as f:
                pred_list = json.load(f)
            if not isinstance(pred_list, list) or not pred_list:
                continue
            hits: List[float] = []
            for p in pred_list:
                if not isinstance(p, dict):
                    continue
                gt_list = p.get("answer") or []
                if isinstance(gt_list, list):
                    gt = {str(s).strip() for s in gt_list if s is not None and str(s).strip()}
                else:
                    gt = set()
                jr = p.get("json_results") if isinstance(p, dict) else None
                preds_set: set[str] = set()
                if isinstance(jr, dict):
                    top3 = jr.get("top3") or []
                    if isinstance(top3, list):
                        preds_set = {str(s).strip() for s in top3 if s is not None and str(s).strip()}
                hit = 1.0 if gt and preds_set and (gt & preds_set) else 0.0
                hits.append(hit)
                p["metrics"] = {"hit_at_3": float(hit)}
            hit_at_3 = (sum(hits) / len(hits)) if hits else 0.0
            out[f"virtual_screening_curated_{subtask}"] = {"hit_at_3": hit_at_3, "n_samples": len(pred_list)}
            _write_json_overwrite(path, pred_list)
        return out


class MolbenchVsEval(BaseEval):
    """Molbench-vs ranking evaluation (top-3 hit rate + averaged rank)."""

    dataset = "molbench-ms-3"
    sub_dataset = "molbench_vs"

    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        preds_dir = os.path.abspath(preds_dir)
        if not os.path.isdir(preds_dir):
            return out
        for fn in sorted(os.listdir(preds_dir)):
            if not fn.endswith(".json"):
                continue
            subtask = os.path.splitext(fn)[0]
            path = os.path.join(preds_dir, fn)
            with open(path, "r", encoding="utf-8") as f:
                pred_list = json.load(f)
            if not isinstance(pred_list, list) or not pred_list:
                continue
            hits: List[float] = []
            hit_nums: List[float] = []
            ranks: List[float] = []
            top3_hit_rates: List[float] = []
            hit_indices: List[str] = []
            for p in pred_list:
                if not isinstance(p, dict):
                    continue
                metrics = _compute_molbench_vs_metrics(p)
                hit = metrics.get("hit_at_3", 0.0)
                hit_num = metrics.get("hit_num", 0.0)
                rank = metrics.get("rank", 4.0)
                top3_rate = metrics.get("top3_hit_rate", 0.0)
                hits.append(hit)
                hit_nums.append(hit_num)
                ranks.append(rank)
                top3_hit_rates.append(top3_rate)
                if hit and p.get("index") is not None:
                    hit_indices.append(str(p.get("index")))
                p["metrics"] = metrics
            total = len(pred_list)
            hit_count = sum(1 for h in hits if h)
            hit_at_3 = (sum(hits) / total) if total else 0.0
            avg_hit_num = (sum(hit_nums) / total) if total else 0.0
            avg_rank = (sum(ranks) / total) if total else 0.0
            avg_top3_hit_rate = (sum(top3_hit_rates) / total) if total else 0.0
            out[f"molbench_vs_{subtask}"] = {
                "hit_at_3": hit_at_3,
                "avg_hit_num": avg_hit_num,
                "avg_rank": avg_rank,
                "top3_hit_rate": avg_top3_hit_rate,
                "hit_count": hit_count,
                "hit_indices": hit_indices,
                "n_samples": total,
            }
            _write_json_overwrite(path, pred_list)
        return out


# ---------- RDKit_bench (list vs list: P/R/F1/sens/spe/acc, validity) ----------


def _normalize_answer_lines(s: str) -> set:
    """Normalize answer to set of non-empty stripped lines for comparison."""
    if not s or not isinstance(s, str):
        return set()
    return {ln.strip() for ln in s.strip().splitlines() if ln.strip()}


def _is_valid_smiles(line: str) -> bool:
    """True if line is valid SMILES (RDKit can parse)."""
    if not line or not isinstance(line, str):
        return False
    try:
        from rdkit import Chem
        mol = Chem.MolFromSmiles(line.strip())
        return mol is not None
    except Exception:
        return False


def _list_metrics(pred: set, gt: set) -> Dict[str, float]:
    """Precision, recall, F1, sensitivity (=recall), specificity (1 if FP==0 else 0)."""
    tp = len(pred & gt)
    fp = len(pred - gt)
    fn = len(gt - pred)
    prec = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    rec = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    spe = 1.0 if fp == 0 else 0.0
    return {"precision": prec, "recall": rec, "f1": f1, "sensitivity": rec, "specificity": spe}


class RdkitBenchEval(BaseEval):
    """RDKit bench: list vs list → precision, recall, f1, sensitivity, specificity, acc; plus validity (format/SMILES)."""

    dataset = "molbench-ms-1"
    sub_dataset = "rdkit_bench"

    def run(self, preds_dir: str, result_dir: str, eval_root: str, **kwargs) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        preds_dir = os.path.abspath(preds_dir)
        if not os.path.isdir(preds_dir):
            return out
        for fn in sorted(os.listdir(preds_dir)):
            if not fn.endswith(".json"):
                continue
            subtask = os.path.splitext(fn)[0]
            path = os.path.join(preds_dir, fn)
            with open(path, "r", encoding="utf-8") as f:
                pred_list = json.load(f)
            if not isinstance(pred_list, list) or not pred_list:
                continue
            n = len(pred_list)
            acc_sum = 0.0
            prec_sum = rec_sum = f1_sum = sens_sum = spe_sum = 0.0
            valid_sum = 0.0
            for p in pred_list:
                gt = _normalize_answer_lines(p.get("gt") or "")
                jr = p.get("json_results") or {}
                pred = _normalize_answer_lines((jr.get("output") or ""))
                hit = 1.0 if pred == gt else 0.0
                acc_sum += hit
                m = _list_metrics(pred, gt)
                prec_sum += m["precision"]
                rec_sum += m["recall"]
                f1_sum += m["f1"]
                sens_sum += m["sensitivity"]
                spe_sum += m["specificity"]
                # Validity: fraction of predicted lines that are valid SMILES
                pred_lines = [ln.strip() for ln in (jr.get("output") or "").strip().splitlines() if ln.strip()]
                valid_frac = (sum(1 for ln in pred_lines if _is_valid_smiles(ln)) / len(pred_lines)) if pred_lines else 0.0
                valid_sum += valid_frac
                if isinstance(p, dict):
                    p["metrics"] = {"acc": float(hit), "precision": m["precision"], "recall": m["recall"], "f1": m["f1"], "sensitivity": m["sensitivity"], "specificity": m["specificity"], "validity": valid_frac}
            out[f"rdkit_bench_{subtask}"] = {
                "acc": acc_sum / n,
                "precision": prec_sum / n,
                "recall": rec_sum / n,
                "f1": f1_sum / n,
                "sensitivity": sens_sum / n,
                "specificity": spe_sum / n,
                "validity": valid_sum / n,
                "n_samples": n,
            }
            _write_json_overwrite(path, pred_list)
        return out
