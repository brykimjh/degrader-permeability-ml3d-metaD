import argparse
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, explained_variance_score
from sklearn.inspection import permutation_importance
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from scipy.stats import pearsonr
from tqdm import tqdm


def load_data(csv_path):
    df = pd.read_csv(csv_path)
    y = df["P_appLog"]

    features_2d = [
        col for col in df.columns if col not in [
            "P_appLog",
            "Ensemble_Average_PSA_Chloroform_ANI",
            "Ensemble_Average_Num_IMHB_Chloroform_ANI",
            "Ensemble_Average_RadiusOfGyration_Chloroform_ANI"
        ]
    ]
    features_3d = [
        "Ensemble_Average_PSA_Chloroform_ANI",
        "Ensemble_Average_Num_IMHB_Chloroform_ANI",
        "Ensemble_Average_RadiusOfGyration_Chloroform_ANI"
    ]

    feature_sets = {
        "2d": features_2d,
        "3d": features_3d,
        "combined": features_2d + features_3d
    }

    return df, y, feature_sets


def evaluate_model(model_type, features, y, outdir,
                   scrambled=False, n_splits=100, test_size=0.5,
                   n_estimators=100, max_depth=None,
                   n_components=2, svr_params=None,
                   perm_repeats=10, model_args_for_config=None):

    feature_names = list(features.columns)
    metric_rows = []
    feature_rows = []

    for i in tqdm(range(1, n_splits + 1), desc=model_type.upper()):
        rng = np.random.RandomState(i)
        y_used = y.sample(frac=1.0, random_state=rng).reset_index(drop=True) if scrambled else y.copy()
        X_train, X_test, y_train, y_test = train_test_split(features, y_used, test_size=test_size, random_state=i)

        if model_type in ["pls", "svr"]:
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
        else:
            X_train_scaled, X_test_scaled = X_train, X_test

        if model_type == "pls":
            model = PLSRegression(n_components=n_components)
        elif model_type == "svr":
            model = SVR(**(svr_params or {}))
        elif model_type == "rf":
            model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=i,
                n_jobs=-1
            )
        else:
            raise ValueError("Unsupported model type")

        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)

        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        pearson_r, _ = pearsonr(y_test, y_pred)
        evs = explained_variance_score(y_test, y_pred)

        metric_rows.append({
            "Split": i,
            "R2": r2,
            "RMSE": rmse,
            "Pearson_r": pearson_r,
            "Pearson_r2": pearson_r ** 2,
            "ExplainedVariance": evs
        })

        result = permutation_importance(model, X_test_scaled, y_test, n_repeats=perm_repeats, random_state=i)
        importances = result.importances_mean
        feature_rows.append(dict(zip(["Split"] + feature_names, [i] + list(importances))))

    # Save metrics
    df_metrics = pd.DataFrame(metric_rows)
    df_metrics.to_csv(os.path.join(outdir, "metrics.csv"), index=False)

    # Save summary metrics
    df_summary_metrics = df_metrics.drop(columns="Split").agg(["mean", "std"]).T.reset_index()
    df_summary_metrics.columns = ["Metric", "Mean", "StdDev"]
    df_summary_metrics.to_csv(os.path.join(outdir, "metrics_summary.csv"), index=False)

    # Save permutation importances
    df_features = pd.DataFrame(feature_rows)
    df_features.to_csv(os.path.join(outdir, "feature_importances.csv"), index=False)

    # Save summary importances
    df_long = df_features.melt(id_vars="Split", var_name="Feature", value_name="Importance")
    df_summary_importances = (
        df_long
        .groupby("Feature", sort=False)["Importance"]
        .mean()
        .reset_index()
        .rename(columns={"Importance": "MeanImportance"})
    )
    df_summary_importances.to_csv(os.path.join(outdir, "feature_importances_summary.csv"), index=False)

    # Save config
    df_config = pd.DataFrame([model_args_for_config])
    df_config.to_csv(os.path.join(outdir, "model_config.csv"), index=False)

    print(f"\n=== Final Summary ===")
    for _, row in df_summary_metrics.iterrows():
        print(f"{row['Metric']:<20}: {row['Mean']:.4f} ± {row['StdDev']:.4f}")
    print(f"\nSaved all output files to: {outdir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=["pls", "svr", "rf"])
    parser.add_argument("--features", default="combined", choices=["2d", "3d", "combined"])
    parser.add_argument("--csv", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--scrambled", action="store_true")
    parser.add_argument("--splits", type=int, default=100)
    parser.add_argument("--test_size", type=float, default=0.5)
    parser.add_argument("--n_estimators", type=int, default=10)
    parser.add_argument("--max_depth", type=int, default=5)
    parser.add_argument("--n_components", type=int, default=2)
    parser.add_argument("--svr_C", type=float, default=1.0)
    parser.add_argument("--svr_epsilon", type=float, default=0.1)
    parser.add_argument("--perm_repeats", type=int, default=10)
    args = parser.parse_args()

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    df, y, feature_sets = load_data(args.csv)
    X = df[feature_sets[args.features]]

    svr_params = {"kernel": "rbf", "C": args.svr_C, "epsilon": args.svr_epsilon}

    model_args_for_config = {
        "model": args.model,
        "features": args.features,
        "scrambled": args.scrambled,
        "splits": args.splits,
        "test_size": args.test_size,
        "n_components": args.n_components if args.model == "pls" else "NA",
        "n_estimators": args.n_estimators if args.model == "rf" else "NA",
        "max_depth": args.max_depth if args.model == "rf" else "NA",
        "svr_C": args.svr_C if args.model == "svr" else "NA",
        "svr_epsilon": args.svr_epsilon if args.model == "svr" else "NA",
        "perm_repeats": args.perm_repeats
    }

    evaluate_model(
        model_type=args.model,
        features=X,
        y=y,
        outdir=outdir,
        scrambled=args.scrambled,
        n_splits=args.splits,
        test_size=args.test_size,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        n_components=args.n_components,
        svr_params=svr_params,
        perm_repeats=args.perm_repeats,
        model_args_for_config=model_args_for_config
    )

