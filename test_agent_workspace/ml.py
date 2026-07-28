"""Machine Learning utilities module."""

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import BaseModel


class ModelConfig(BaseModel):
    """Configuration for a machine learning model."""

    name: str
    version: str
    model_type: str
    hyperparameters: dict[str, Any]
    metadata: dict[str, Any] = {}


class TrainingMetrics(BaseModel):
    """Metrics from a training run."""

    epoch: int
    train_loss: float
    val_loss: float | None = None
    train_accuracy: float | None = None
    val_accuracy: float | None = None
    learning_rate: float | None = None


class MLModel:
    """Base class for machine learning models."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.is_trained = False
        self.metrics_history: list[TrainingMetrics] = []

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 10) -> list[TrainingMetrics]:
        """Train the model. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement train method")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement predict method")

    def save(self, path: str | Path) -> None:
        """Save model to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            "config": self.config.model_dump(),
            "metrics_history": [m.model_dump() for m in self.metrics_history],
            "is_trained": self.is_trained,
        }

        with open(path, "wb") as f:
            pickle.dump(model_data, f)

    @classmethod
    def load(cls, path: str | Path) -> "MLModel":
        """Load model from disk."""
        with open(path, "rb") as f:
            model_data = pickle.load(f)

        config = ModelConfig(**model_data["config"])
        model = cls(config)
        model.is_trained = model_data["is_trained"]
        model.metrics_history = [TrainingMetrics(**m) for m in model_data["metrics_history"]]
        return model


class LinearRegressionModel(MLModel):
    """Simple linear regression implementation."""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.weights: np.ndarray | None = None
        self.bias: float = 0.0

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 100,
        learning_rate: float = 0.01,
    ) -> list[TrainingMetrics]:
        """Train using gradient descent."""
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0.0

        self.metrics_history = []

        for epoch in range(epochs):
            # Forward pass
            y_pred = np.dot(X, self.weights) + self.bias

            # Compute loss (MSE)
            loss = np.mean((y_pred - y) ** 2)

            # Compute gradients
            dw = (2 / n_samples) * np.dot(X.T, (y_pred - y))
            db = (2 / n_samples) * np.sum(y_pred - y)

            # Update parameters
            self.weights -= learning_rate * dw
            self.bias -= learning_rate * db

            # Record metrics
            metrics = TrainingMetrics(
                epoch=epoch,
                train_loss=loss,
                learning_rate=learning_rate,
            )
            self.metrics_history.append(metrics)

        self.is_trained = True
        return self.metrics_history

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
        return np.dot(X, self.weights) + self.bias


def create_model(config_dict: dict[str, Any]) -> MLModel:
    """Factory function to create models from config."""
    config = ModelConfig(**config_dict)

    if config.model_type == "linear_regression":
        return LinearRegressionModel(config)
    else:
        raise ValueError(f"Unknown model type: {config.model_type}")


def load_dataset(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Load dataset from CSV file."""
    path = Path(path)
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    X = data[:, :-1]
    y = data[:, -1]
    return X, y


def train_test_split(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split dataset into train and test sets."""
    if random_state is not None:
        np.random.seed(random_state)

    n_samples = X.shape[0]
    indices = np.random.permutation(n_samples)
    split_idx = int(n_samples * (1 - test_size))

    train_indices = indices[:split_idx]
    test_indices = indices[split_idx:]

    return X[train_indices], X[test_indices], y[train_indices], y[test_indices]


def mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute mean squared error."""
    return float(np.mean((y_true - y_pred) ** 2))


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute R-squared score."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1 - (ss_res / ss_tot))