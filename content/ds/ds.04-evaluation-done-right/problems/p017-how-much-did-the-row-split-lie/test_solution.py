import pytest
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier

from conftest import make_patients
from solution import row_vs_group_cv


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_row_split_is_optimistic(seed):
    X, y, pid = make_patients(seed=seed)
    row, grp = row_vs_group_cv(X, y, pid, KNeighborsClassifier(5))
    assert row > 0.68, f"row-wise CV lets the model recognise patients: AUC about 0.75, got {row:.3f}."
    assert row - grp > 0.12, f"row {row:.3f} vs group {grp:.3f}: the group split must be clearly lower. Pass groups= to GroupKFold."


def test_group_score_matches_group_kfold():
    X, y, pid = make_patients(seed=4)
    _, grp = row_vs_group_cv(X, y, pid, KNeighborsClassifier(5))
    direct = cross_val_score(KNeighborsClassifier(5), X, y, cv=GroupKFold(5), groups=pid, scoring="roc_auc").mean()
    assert grp == pytest.approx(direct), "group_auc = mean of cross_val_score with GroupKFold(5) and groups."
