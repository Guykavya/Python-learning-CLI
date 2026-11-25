from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler


def lasso_selected(X, y, alpha):
    if alpha < 0:
        raise ValueError("alpha must be non-negative")
    Z = StandardScaler().fit_transform(X)
    coef = Lasso(alpha=alpha).fit(Z, y).coef_
    return [name for name, c in zip(X.columns, coef) if c != 0]
