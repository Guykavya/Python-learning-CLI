import numpy as np


def cuped(df, y="converted", x="pre_orders_90d"):
    yv, xv = df[y].astype(float).to_numpy(), df[x].astype(float).to_numpy()
    theta = np.cov(yv, xv)[0, 1] / np.var(xv, ddof=1)
    adjusted = yv - theta * (xv - xv.mean())
    return adjusted, float(theta), float(np.corrcoef(yv, xv)[0, 1] ** 2)
