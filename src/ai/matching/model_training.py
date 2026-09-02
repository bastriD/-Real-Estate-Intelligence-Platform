from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.ai.matching.dataset_split import (
    DatasetSplit,
    GROUP_COLUMN,
)
from src.ai.matching.evaluate import (
    DEFAULT_RANKING_KS,
    compute_ranking_metrics,
)
from src.ai.matching.training_dataset import (
    FEATURE_COLUMNS,
    LABEL_COLUMN,
)


REFERENCE_COLUMN = "reference_externe"
PREDICTION_COLUMN = "predicted_relevance"
PROBABILITY_COLUMN = "relevance_probability"

DEFAULT_CLASSIFICATION_THRESHOLD = 0.5
DEFAULT_MAX_ITERATIONS = 1000


@dataclass(frozen=True)
class SupervisedModelResult:
    """
    Result of one supervised matching-model training run.

    The model is trained exclusively on the train partition.

    Validation and test partitions are used only for evaluation.
    """

    model: LogisticRegression

    feature_columns: tuple[str, ...]

    train_predictions: pd.DataFrame
    validation_predictions: pd.DataFrame
    test_predictions: pd.DataFrame

    train_metrics: dict[str, Any]
    validation_metrics: dict[str, Any]
    test_metrics: dict[str, Any]


def _validate_model_dataset(
    dataset: pd.DataFrame,
) -> None:
    """
    Validate that a dataset partition can safely be used by the model.

    Only the canonical deterministic matching feature columns are accepted
    as model inputs.

    Metadata and lineage columns remain available in the DataFrame for
    evaluation and traceability but are never passed to the estimator.
    """

    if dataset.empty:
        raise ValueError(
            "Cannot train or evaluate the model on an empty dataset."
        )

    required_columns = {
        GROUP_COLUMN,
        REFERENCE_COLUMN,
        LABEL_COLUMN,
        *FEATURE_COLUMNS,
    }

    missing_columns = required_columns.difference(
        dataset.columns
    )

    if missing_columns:
        raise ValueError(
            "Dataset is missing required model columns: "
            + ", ".join(sorted(missing_columns))
        )

    if dataset[GROUP_COLUMN].isna().any():
        raise ValueError(
            f"Dataset contains null values in {GROUP_COLUMN}."
        )

    if dataset[REFERENCE_COLUMN].isna().any():
        raise ValueError(
            f"Dataset contains null values in {REFERENCE_COLUMN}."
        )

    if dataset[LABEL_COLUMN].isna().any():
        raise ValueError(
            f"Dataset contains null values in {LABEL_COLUMN}."
        )

    labels = set(
        dataset[LABEL_COLUMN]
        .astype(int)
        .unique()
        .tolist()
    )

    if labels != {0, 1}:
        raise ValueError(
            "Model dataset must contain both binary classes {0, 1}. "
            f"Classes found: {sorted(labels)}"
        )

    feature_frame = dataset[FEATURE_COLUMNS]

    if feature_frame.isna().any().any():
        null_columns = (
            feature_frame.columns[
                feature_frame.isna().any()
            ]
            .tolist()
        )

        raise ValueError(
            "Model features contain null values: "
            + ", ".join(null_columns)
        )

    feature_values = feature_frame.to_numpy(
        dtype=float
    )

    if not np.isfinite(feature_values).all():
        raise ValueError(
            "Model features contain non-finite values."
        )

    if (
        (feature_values < 0.0).any()
        or (feature_values > 1.0).any()
    ):
        raise ValueError(
            "Canonical matching features must remain inside [0, 1]."
        )


def build_model_matrix(
    dataset: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Extract the canonical model matrix and binary target.

    This is the single feature-selection boundary for supervised matching.

    No metadata, lineage identifier or ground-truth reference can enter X.
    """

    _validate_model_dataset(dataset)

    features = dataset[
        FEATURE_COLUMNS
    ].astype(float).copy()

    target = dataset[
        LABEL_COLUMN
    ].astype(int).copy()

    if list(features.columns) != FEATURE_COLUMNS:
        raise AssertionError(
            "Unexpected supervised feature ordering."
        )

    return features, target


def train_logistic_regression(
    train_dataset: pd.DataFrame,
    *,
    random_state: int = 42,
    max_iter: int = DEFAULT_MAX_ITERATIONS,
) -> LogisticRegression:
    """
    Train the first explainable supervised matching baseline.

    Logistic Regression is intentionally used as the initial ML baseline:
    simple, reproducible, interpretable and easy to compare against the
    deterministic ranking baseline.
    """

    features, target = build_model_matrix(
        train_dataset
    )

    model = LogisticRegression(
        random_state=random_state,
        max_iter=max_iter,
        solver="lbfgs",
    )

    model.fit(
        features,
        target,
    )

    return model


def predict_relevance(
    model: LogisticRegression,
    dataset: pd.DataFrame,
    *,
    threshold: float = DEFAULT_CLASSIFICATION_THRESHOLD,
) -> pd.DataFrame:
    """
    Produce relevance probabilities and binary predictions.

    The returned frame preserves group/reference/label metadata so ranking
    evaluation can be performed per demande_version.
    """

    if not 0.0 < threshold < 1.0:
        raise ValueError(
            "Classification threshold must be between 0 and 1."
        )

    features, _ = build_model_matrix(
        dataset
    )

    if not hasattr(model, "classes_"):
        raise ValueError(
            "The supplied LogisticRegression model is not fitted."
        )

    classes = list(
        int(value)
        for value in model.classes_
    )

    if classes != [0, 1]:
        raise ValueError(
            "Expected fitted classifier classes [0, 1]. "
            f"Classes found: {classes}"
        )

    probabilities = model.predict_proba(
        features
    )[:, 1]

    predictions = (
        probabilities >= threshold
    ).astype(int)

    result = dataset.copy()

    result[PROBABILITY_COLUMN] = probabilities
    result[PREDICTION_COLUMN] = predictions

    return result


def compute_classification_metrics(
    predictions: pd.DataFrame,
) -> dict[str, float]:
    """
    Compute standard binary classification metrics.

    These complement ranking metrics; they do not replace them.
    """

    required_columns = {
        LABEL_COLUMN,
        PREDICTION_COLUMN,
        PROBABILITY_COLUMN,
    }

    missing_columns = required_columns.difference(
        predictions.columns
    )

    if missing_columns:
        raise ValueError(
            "Prediction dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    y_true = predictions[
        LABEL_COLUMN
    ].astype(int)

    y_pred = predictions[
        PREDICTION_COLUMN
    ].astype(int)

    y_probability = predictions[
        PROBABILITY_COLUMN
    ].astype(float)

    classes = set(
        y_true.unique().tolist()
    )

    if classes != {0, 1}:
        raise ValueError(
            "Classification metrics require both classes."
        )

    return {
        "accuracy": float(
            accuracy_score(
                y_true,
                y_pred,
            )
        ),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_true,
                y_probability,
            )
        ),
        "average_precision": float(
            average_precision_score(
                y_true,
                y_probability,
            )
        ),
        "log_loss": float(
            log_loss(
                y_true,
                y_probability,
                labels=[0, 1],
            )
        ),
    }


def _compute_group_ranking_metrics(
    group: pd.DataFrame,
    *,
    ks: tuple[int, ...],
) -> dict[str, float]:
    """
    Evaluate one demande_version as one independent ranking problem.
    """

    if group.empty:
        raise ValueError(
            "Cannot evaluate ranking metrics on an empty group."
        )

    ground_truth = set(
        group.loc[
            group[LABEL_COLUMN].astype(int) == 1,
            REFERENCE_COLUMN,
        ]
        .astype(str)
        .tolist()
    )

    if not ground_truth:
        raise ValueError(
            "Ranking evaluation group contains no positive examples."
        )

    ranked = (
        group.sort_values(
            by=[
                PROBABILITY_COLUMN,
                REFERENCE_COLUMN,
            ],
            ascending=[
                False,
                True,
            ],
            kind="mergesort",
        )
        .reset_index(drop=True)
    )

    return compute_ranking_metrics(
        ranked=ranked,
        ground_truth=ground_truth,
        ks=ks,
    )


def compute_grouped_ranking_metrics(
    predictions: pd.DataFrame,
    *,
    ks: tuple[int, ...] = DEFAULT_RANKING_KS,
) -> dict[str, Any]:
    """
    Compute ranking metrics independently for every demande_version.

    Aggregate metrics are macro averages over search groups so that a
    demande_version with many candidates cannot dominate the evaluation.
    """

    required_columns = {
        GROUP_COLUMN,
        REFERENCE_COLUMN,
        LABEL_COLUMN,
        PROBABILITY_COLUMN,
    }

    missing_columns = required_columns.difference(
        predictions.columns
    )

    if missing_columns:
        raise ValueError(
            "Ranking prediction dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if not ks:
        raise ValueError(
            "At least one ranking cutoff k is required."
        )

    group_metrics: dict[str, dict[str, float]] = {}

    for group_id, group in predictions.groupby(
        GROUP_COLUMN,
        sort=True,
    ):
        metrics = _compute_group_ranking_metrics(
            group,
            ks=ks,
        )

        group_metrics[str(int(group_id))] = {
            metric_name: float(metric_value)
            for metric_name, metric_value in metrics.items()
        }

    if not group_metrics:
        raise ValueError(
            "No demande_version groups available for ranking evaluation."
        )

    metric_names = sorted(
        next(
            iter(group_metrics.values())
        ).keys()
    )

    macro_average = {
        metric_name: float(
            np.mean(
                [
                    metrics[metric_name]
                    for metrics in group_metrics.values()
                ]
            )
        )
        for metric_name in metric_names
    }

    return {
        "group_count": len(group_metrics),
        "aggregation": "macro_average_by_id_demande_version",
        "macro_average": macro_average,
        "per_group": group_metrics,
    }


def evaluate_predictions(
    predictions: pd.DataFrame,
    *,
    ks: tuple[int, ...] = DEFAULT_RANKING_KS,
) -> dict[str, Any]:
    """
    Evaluate one model partition using both classification and ranking
    perspectives.
    """

    return {
        "rows": len(predictions),
        "groups": int(
            predictions[GROUP_COLUMN].nunique()
        ),
        "classification": (
            compute_classification_metrics(
                predictions
            )
        ),
        "ranking": (
            compute_grouped_ranking_metrics(
                predictions,
                ks=ks,
            )
        ),
    }


def train_and_evaluate_logistic_regression(
    split: DatasetSplit,
    *,
    random_state: int = 42,
    threshold: float = DEFAULT_CLASSIFICATION_THRESHOLD,
    ks: tuple[int, ...] = DEFAULT_RANKING_KS,
) -> SupervisedModelResult:
    """
    Train Logistic Regression exclusively on split.train and evaluate the
    resulting frozen model on train, validation and test.

    No fitting occurs on validation or test data.
    """

    model = train_logistic_regression(
        train_dataset=split.train,
        random_state=random_state,
    )

    train_predictions = predict_relevance(
        model=model,
        dataset=split.train,
        threshold=threshold,
    )

    validation_predictions = predict_relevance(
        model=model,
        dataset=split.validation,
        threshold=threshold,
    )

    test_predictions = predict_relevance(
        model=model,
        dataset=split.test,
        threshold=threshold,
    )

    train_metrics = evaluate_predictions(
        train_predictions,
        ks=ks,
    )

    validation_metrics = evaluate_predictions(
        validation_predictions,
        ks=ks,
    )

    test_metrics = evaluate_predictions(
        test_predictions,
        ks=ks,
    )

    return SupervisedModelResult(
        model=model,
        feature_columns=tuple(
            FEATURE_COLUMNS
        ),
        train_predictions=train_predictions,
        validation_predictions=validation_predictions,
        test_predictions=test_predictions,
        train_metrics=train_metrics,
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
    )


def model_coefficients(
    result: SupervisedModelResult,
) -> dict[str, float]:
    """
    Expose Logistic Regression coefficients for interpretability evidence.
    """

    coefficients = result.model.coef_

    if coefficients.shape != (
        1,
        len(result.feature_columns),
    ):
        raise AssertionError(
            "Unexpected Logistic Regression coefficient shape."
        )

    return {
        feature_name: float(coefficient)
        for feature_name, coefficient in zip(
            result.feature_columns,
            coefficients[0],
            strict=True,
        )
    }


def model_metadata(
    result: SupervisedModelResult,
) -> dict[str, Any]:
    """
    Produce serializable technical metadata for later artifact and MLflow
    tracking.
    """

    return {
        "model_type": "LogisticRegression",
        "library": "scikit-learn",
        "feature_columns": list(
            result.feature_columns
        ),
        "label_column": LABEL_COLUMN,
        "group_column": GROUP_COLUMN,
        "reference_column": REFERENCE_COLUMN,
        "classification_threshold": (
            DEFAULT_CLASSIFICATION_THRESHOLD
        ),
        "ground_truth_used_as_feature": False,
        "group_metadata_used_as_feature": False,
        "lineage_metadata_used_as_feature": False,
        "coefficients": model_coefficients(
            result
        ),
        "intercept": float(
            result.model.intercept_[0]
        ),
    }