from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest


def main() -> None:
    rng = np.random.default_rng(42)
    normal = np.column_stack(
        [
            rng.normal(120, 55, 5000),
            rng.binomial(1, 0.1, 5000),
            rng.normal(2200, 900, 5000),
        ]
    )
    model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
    model.fit(normal)

    output = Path("ml/isolation_forest.joblib")
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output)
    print(f"Saved model to {output}")


if __name__ == "__main__":
    main()
