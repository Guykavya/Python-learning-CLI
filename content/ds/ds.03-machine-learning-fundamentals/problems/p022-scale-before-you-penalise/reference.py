from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def ridge_pipeline(alpha):
    return make_pipeline(StandardScaler(), Ridge(alpha=alpha))
