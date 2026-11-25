import math

import numpy as np
import pandas as pd
from sklearn import dummy, metrics, model_selection


class TestSetAlreadyOpened(RuntimeError):
    pass


class Evaluation:
    def __init__(self, X, y, task="regression", test_size=0.2, seed=0):
        if task not in ("regression", "classification"):
            raise ValueError("task must be 'regression' or 'classification'")
        self.task, self.seed = task, seed
        strat = y if task == "classification" else None
        self.X_dev, self._X_test, self.y_dev, self._y_test = model_selection.train_test_split(
            X, y, test_size=test_size, random_state=seed, stratify=strat)
        self._opened = False
        self.cv = (model_selection.StratifiedKFold(5, shuffle=True, random_state=seed) if task == "classification"
                   else model_selection.KFold(5, shuffle=True, random_state=seed))
        self.scoring = "accuracy" if task == "classification" else "neg_root_mean_squared_error"

    def compare(self, models):
        rows = []
        for name, m in models.items():
            s = model_selection.cross_val_score(m, self.X_dev, self.y_dev, cv=self.cv, scoring=self.scoring)
            s = s if self.task == "classification" else -s
            rows.append({"model": name, "cv_mean": float(s.mean()), "cv_sd": float(s.std(ddof=1))})
        ascending = self.task == "regression"
        return pd.DataFrame(rows).sort_values("cv_mean", ascending=ascending).reset_index(drop=True)

    def baseline(self):
        base = (dummy.DummyClassifier(strategy="most_frequent") if self.task == "classification"
                else dummy.DummyRegressor())
        return self.compare({"baseline": base}).iloc[0]

    def learning_curve(self, model, sizes=(0.1, 0.25, 0.5, 0.75, 1.0)):
        n, tr, va = model_selection.learning_curve(model, self.X_dev, self.y_dev, train_sizes=list(sizes),
                                                   cv=self.cv, scoring=self.scoring)
        sign = 1 if self.task == "classification" else -1
        lc = pd.DataFrame({"n_train": n, "train": sign * tr.mean(axis=1), "validation": sign * va.mean(axis=1)})
        lc["gap"] = (lc["train"] - lc["validation"]) if self.task == "classification" else (lc["validation"] - lc["train"])
        return lc

    @staticmethod
    def diagnose(lc, task="regression"):
        last = lc.iloc[-1]
        err = (1 - last["validation"]) if task == "classification" else last["validation"]
        rel_gap = last["gap"] / max(abs(err), 1e-12)
        if rel_gap > 0.15:
            return "high variance (large gap between training and validation): more data, simpler model or regularisation"
        return "high bias or near the noise floor (small gap): more capacity or better features, not more data"

    def tune(self, model, grid):
        gs = model_selection.GridSearchCV(model, grid, cv=self.cv, scoring=self.scoring).fit(self.X_dev, self.y_dev)
        return gs.best_estimator_, gs.best_params_, abs(gs.best_score_)

    def final_test(self, model):
        if self._opened:
            raise TestSetAlreadyOpened("the test set was already used once; collect new data instead of tuning on it")
        self._opened = True
        model.fit(self.X_dev, self.y_dev)
        p = model.predict(self._X_test)
        if self.task == "regression":
            return {"RMSE": float(math.sqrt(metrics.mean_squared_error(self._y_test, p))),
                    "MAE": float(metrics.mean_absolute_error(self._y_test, p)),
                    "R2": float(metrics.r2_score(self._y_test, p))}
        return {"accuracy": float(metrics.accuracy_score(self._y_test, p)),
                "precision": float(metrics.precision_score(self._y_test, p, average="macro")),
                "recall": float(metrics.recall_score(self._y_test, p, average="macro")),
                "F1": float(metrics.f1_score(self._y_test, p, average="macro"))}
