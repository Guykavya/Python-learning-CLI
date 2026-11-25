from sklearn.preprocessing import StandardScaler


def scale_split(X_train, X_test):
    scaler = StandardScaler().fit(X_train)
    return scaler.transform(X_train), scaler.transform(X_test)
