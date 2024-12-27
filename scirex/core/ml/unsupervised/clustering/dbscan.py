# Copyright (c) 2024 Zenteiq Aitech Innovations Private Limited and AiREX Lab,
# Indian Institute of Science, Bangalore.
# All rights reserved.
#
# This file is part of SciREX
# (Scientific Research and Engineering eXcellence Platform),
# developed jointly by Zenteiq Aitech Innovations and AiREX Lab
# under the guidance of Prof. Sashikumaar Ganesan.
#
# SciREX is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SciREX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with SciREX. If not, see <https://www.gnu.org/licenses/>.
#
# For any clarifications or special considerations,
# please contact <scirex@zenteiq.ai>

# Author: Dev Sahoo
# Linkedin: https://www.linkedin.com/in/debajyoti-sahoo13/

"""DBSCAN Clustering Implementation.

This module provides a DBSCAN clustering implementation using scikit-learn's DBSCAN class.

It includes an optional automated heuristic for estimating `eps` and `min_samples`
by analyzing neighborhood distances. The user can override these defaults before fitting.
"""

# Standard library imports
from typing import Dict, Any, Optional

# Third-party imports
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

# Local imports
from base import Clustering


class Dbscan(Clustering):
    """
    DBSCAN clustering algorithm with optional automatic estimation of `eps` and `min_samples`.

    Attributes:
        eps (Optional[float]): The maximum neighborhood distance after estimation/user input.
        min_samples (Optional[int]): The number of samples in a neighborhood for
                                     a point to be considered a core point.
        n_clusters (Optional[int]): The number of clusters found (excluding noise).
        n_noise (Optional[int]): The number of noise points labeled as -1 by DBSCAN.
    """

    def __init__(self) -> None:
        """
        Initialize the DBSCAN clustering model.

        By default, `eps` and `min_samples` are not set until the user calls `.fit(...)`.
        The final values are determined by a heuristic (plus optional user override).
        """
        super().__init__("dbscan")
        self.eps: Optional[float] = None
        self.min_samples: Optional[int] = None
        self.n_clusters: Optional[int] = None
        self.n_noise: Optional[int] = None

    def fit(self, X: np.ndarray) -> None:
        """
        Fit the DBSCAN model to the data with a heuristic approach to determine eps and min_samples.

        Args:
            X (np.ndarray): Input data array of shape (n_samples, n_features).
        """
        X = X.astype(np.float32, copy=False)
        n_samples = X.shape[0]
        rng = np.random.default_rng(self.random_state)

        # Heuristic for min_samples
        self.min_samples = max(5, int(np.log2(n_samples)) + 1)

        # Subsample for k-distance estimation
        sample_size = min(1000, n_samples)
        indices = rng.choice(n_samples, sample_size, replace=False)
        X_sample = X[indices]

        # Compute k-distance (k = min_samples)
        nbrs = NearestNeighbors(n_neighbors=self.min_samples)
        nbrs.fit(X_sample)
        distances, _ = nbrs.kneighbors(X_sample)
        k_distances = distances[
            :, -1
        ]  # The distance to the min_samples-th nearest neighbor
        self.eps = float(np.median(k_distances))

        print("Estimated parameters from heuristic:")
        print(f"eps = {self.eps:.4f}, min_samples = {self.min_samples}")

        # Optional user override
        user_input = (
            input("Do you want to input your own 'eps' and 'min_samples'? (y/n): ")
            .strip()
            .lower()
        )
        if user_input == "y":
            eps_input = input(f"Enter 'eps' (current estimate is {self.eps:.4f}): ")
            min_samples_input = input(
                f"Enter 'min_samples' (current estimate is {self.min_samples}): "
            )
            self.eps = float(eps_input)
            self.min_samples = int(min_samples_input)

        # Fit DBSCAN
        self.model = DBSCAN(eps=self.eps, min_samples=self.min_samples)
        self.labels = self.model.fit_predict(X)

        # Compute the number of clusters (excluding noise)
        self.n_clusters = len(set(self.labels)) - (1 if -1 in self.labels else 0)
        self.n_noise = np.count_nonzero(self.labels == -1)

        print(
            f"DBSCAN fitted with eps = {self.eps:.4f}, min_samples = {self.min_samples}"
        )
        print(f"Number of clusters found: {self.n_clusters}")
        print(f"Number of noise points: {self.n_noise}")

    def get_model_params(self) -> Dict[str, Any]:
        """
        Get parameters of the fitted DBSCAN model.

        Returns:
            Dict[str, Any]:
                A dictionary containing:
                - model_type (str)
                - eps (float)
                - min_samples (int)
                - n_clusters (int)
        """
        return {
            "model_type": self.model_type,
            "eps": self.eps,
            "min_samples": self.min_samples,
            "n_clusters": self.n_clusters,
        }