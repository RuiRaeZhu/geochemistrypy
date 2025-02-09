# -*- coding: utf-8 -*-
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
from sklearn.cluster import AffinityPropagation
from utils.base import save_data
from utils.base import save_fig
from global_variable import MODEL_OUTPUT_IMAGE_PATH
from global_variable import DATASET_OUTPUT_PATH
from ._base import WorkflowBase
from .func.algo_clustering._cluster import plot_silhouette_diagram, scatter2d, scatter3d
from .func.algo_clustering._dbscan import dbscan_result_plot
from typing import Optional, Union, Dict
from abc import ABCMeta, abstractmethod


class ClusteringWorkflowBase(WorkflowBase):
    """Base class for Cluster.

    Warning: This class should not be used directly.
    Use derived classes instead.
    """
    common_function = ['Cluster Centers',
                       'Cluster Labels',
                       ]

    def __init__(self):
        super().__init__()

    def fit(self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None) -> None:
        self.X = X
        self.model.fit(X)

    def get_cluster_centers(self) -> np.ndarray:
        print("-----* Clustering Centers *-----")
        print(getattr(self.model, 'cluster_centers_', 'This class don not have cluster_centers_'))
        return getattr(self.model, 'cluster_centers_', 'This class don not have cluster_centers_')

    def get_labels(self):
        print("-----* Clustering Labels *-----")
        self.X['clustering result'] = self.model.labels_
        print(self.X)
        save_data(self.X, f"{self.naming}", DATASET_OUTPUT_PATH)


class KMeansClustering(ClusteringWorkflowBase):

    name = "KMeans"
    special_function = ['KMeans Score']

    def __init__(self,
                 n_clusters=8,
                 init="k-means++",
                 n_init=10,
                 max_iter=300,
                 tol=1e-4,
                 verbose=0,
                 random_state=None,
                 copy_x=True,
                 algorithm="auto"):
        """
        Parameters
        ----------
        n_clusters : int, default=8
            The number of clusters to form as well as the number of
            centroids to generate.

        init : {'k-means++', 'random'}, callable or array-like of shape \
                (n_clusters, n_features), default='k-means++'
            Method for initialization:

            'k-means++' : selects initial cluster centers for k-mean
            clustering in a smart way to speed up convergence. See section
            Notes in k_init for more details.

            'random': choose `n_clusters` observations (rows) at random from data
            for the initial centroids.

            If an array is passed, it should be of shape (n_clusters, n_features)
            and gives the initial centers.

            If a callable is passed, it should take arguments X, n_clusters and a
            random state and return an initialization.

        n_init : int, default=10
            Number of time the k-means algorithm will be run with different
            centroid seeds. The final results will be the best output of
            n_init consecutive runs in terms of inertia.

        max_iter : int, default=300
            Maximum number of iterations of the k-means algorithm for a
            single run.

        tol : float, default=1e-4
            Relative tolerance with regards to Frobenius norm of the difference
            in the cluster centers of two consecutive iterations to declare
            convergence.

        verbose : int, default=0
            Verbosity mode.

        random_state : int, RandomState instance or None, default=None
            Determines random number generation for centroid initialization. Use
            an int to make the randomness deterministic.
            See :term:`Glossary <random_state>`.

        copy_x : bool, default=True
            When pre-computing distances it is more numerically accurate to center
            the data first. If copy_x is True (default), then the original data is
            not modified. If False, the original data is modified, and put back
            before the function returns, but small numerical differences may be
            introduced by subtracting and then adding the data mean. Note that if
            the original data is not C-contiguous, a copy will be made even if
            copy_x is False. If the original data is sparse, but not in CSR format,
            a copy will be made even if copy_x is False.

        algorithm : {"auto", "full", "elkan"}, default="auto"
            K-means algorithm to use. The classical EM-style algorithm is "full".
            The "elkan" variation is more efficient on data with well-defined
            clusters, by using the triangle inequality. However it's more memory
            intensive due to the allocation of an extra array of shape
            (n_samples, n_clusters).

            For now "auto" (kept for backward compatibility) chooses "elkan" but it
            might change in the future for a better heuristic.

        References
        ----------------------------------------
        Read more in the :ref:`User Guide <k_means>`.
        https://scikit-learn.org/stable/modules/clustering.html#k-means
        """

        super().__init__()
        self.n_clusters = n_clusters
        self.init = init
        self.max_iter = max_iter
        self.tol = tol
        self.n_init = n_init
        self.verbose = verbose
        self.random_state = random_state
        self.copy_x = copy_x
        self.algorithm = algorithm
        self.model = KMeans(n_clusters=self.n_clusters,
                            init=self.init,
                            n_init=self.n_init,
                            max_iter=self.max_iter,
                            tol=self.tol,
                            verbose=self.verbose,
                            random_state=self.random_state,
                            copy_x=self.copy_x,
                            algorithm=self.algorithm)
        self.naming = KMeansClustering.name

    def _get_scores(self):
        print("-----* KMeans Scores *-----")
        print("Inertia Score: ", self.model.inertia_)
        print("Calinski Harabasz Score: ", metrics.calinski_harabasz_score(self.X, self.model.labels_))
        print("Silhouette Score: ", metrics.silhouette_score(self.X, self.model.labels_))

    @staticmethod
    def _plot_silhouette_diagram(data: pd.DataFrame, cluster_labels: pd.DataFrame,cluster_centers_: np.ndarray, n_clusters: int, algorithm_name: str, store_path: str) -> None:
        print("-----* Silhouette Diagram *-----")
        plot_silhouette_diagram(data, cluster_labels, cluster_centers_, n_clusters, algorithm_name)
        save_fig(f"Silhouette Diagram - {algorithm_name}", store_path)

    def _scatter2d(self, data: pd.DataFrame, cluster_labels: pd.DataFrame, algorithm_name: str, store_path: str) -> None:
        print("-----* Bi-plot *-----")
        scatter2d(data, cluster_labels, algorithm_name)
        save_fig(f"Bi-plot - {algorithm_name}", store_path)

    def _scatter3d(self) -> None:
        print("-----* Tri-plot *-----")
        scatter3d()

    def special_components(self, **kwargs: Union[Dict, np.ndarray, int]) -> None:
        self._get_scores()
        self._plot_silhouette_diagram(data=self.X, cluster_labels=self.X['clustering result'],
                                      cluster_centers_=self.get_cluster_centers(), n_clusters=self.n_clusters,
                                      algorithm_name=self.naming, store_path=MODEL_OUTPUT_IMAGE_PATH)
        # Draw graphs when the number of principal components > 3
        if kwargs['components_num'] > 3:
            self._scatter3d()
        elif kwargs['components_num'] == 3:
            self._scatter3d()
        elif kwargs['components_num'] == 2:
            self._scatter2d(data=self.X, cluster_labels=self.X['clustering result'], algorithm_name=self.naming, store_path=MODEL_OUTPUT_IMAGE_PATH)

        else:
            pass


class DBSCANClustering(ClusteringWorkflowBase):

    name = "DBSCAN"
    special_function = ['Virtualization of result in 2D graph']

    def __init__(self,
                 eps=0.5,
                 min_samples=5,
                 metric="euclidean",
                 metric_params=None,
                 algorithm="auto",
                 leaf_size=30,
                 p=None,
                 n_jobs=None,
                 ):
        """
        Parameters
        ----------
        eps : float, default=0.5
        The maximum distance between two samples for one to be considered as in the neighborhood of the other. This is not a maximum bound on the distances of points within a cluster. This is the most important DBSCAN parameter to choose appropriately for your data set and distance function.

        min_samples : int, default=5
        The number of samples (or total weight) in a neighborhood for a point to be considered as a core point. This includes the point itself.

        metric : str, or callable, default=’euclidean’
        The metric to use when calculating distance between instances in a feature array. If metric is a string or callable, it must be one of the options allowed by sklearn.metrics.pairwise_distances for its metric parameter. If metric is “precomputed”, X is assumed to be a distance matrix and must be square. X may be a sparse graph, in which case only “nonzero” elements may be considered neighbors for DBSCAN.

        New in version 0.17: metric precomputed to accept precomputed sparse matrix.

        metric_params : dict, default=None
        Additional keyword arguments for the metric function.

        New in version 0.19.

        algorithm : {‘auto’, ‘ball_tree’, ‘kd_tree’, ‘brute’}, default=’auto’
        The algorithm to be used by the NearestNeighbors module to compute pointwise distances and find nearest neighbors. See NearestNeighbors module documentation for details.

        leaf_size : int, default=30
        Leaf size passed to BallTree or cKDTree. This can affect the speed of the construction and query, as well as the memory required to store the tree. The optimal value depends on the nature of the problem.

        p : float, default=None
        The power of the Minkowski metric to be used to calculate distance between points. If None, then p=2 (equivalent to the Euclidean distance).

        n_jobs : int, default=None
        The number of parallel jobs to run. None means 1 unless in a joblib.parallel_backend context. -1 means using all processors. See Glossary for more details.

        References
        ----------------------------------------
        Read more in the :ref:`User Guide <dbscan>`.
        https://scikit-learn.org/stable/modules/clustering.html#dbscan
        """

        super().__init__()
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric
        self.metric_params = metric_params
        self.algorithm = algorithm
        self.leaf_size = leaf_size
        self.p = p
        self.n_jobs = n_jobs
        self.model = DBSCAN(eps=self.eps,
                            min_samples=self.min_samples,
                            metric=self.metric,
                            metric_params=self.metric_params,
                            algorithm=self.algorithm,
                            leaf_size=self.leaf_size,
                            p=self.p,
                            n_jobs=self.n_jobs)
        self.naming = DBSCANClustering.name

    @staticmethod
    def clustering_result_plot(X: pd.DataFrame, trained_model: any, algorithm_name: str, store_path: str) -> None:
        print("-------** dbscan_clustering_result_2d_plot **----------")
        dbscan_result_plot(X, trained_model, algorithm_name)
        save_fig(f'Plot - {algorithm_name} - 2D', store_path)

    def special_components(self, **kwargs: Union[Dict, np.ndarray, int]) -> None:
        self.clustering_result_plot(self.X, self.model, self.naming, MODEL_OUTPUT_IMAGE_PATH)


class AffinityPropagationClustering(ClusteringWorkflowBase):
    name = "AffinityPropagation"

    def __init__(self,
                 *,
                 damping=0.5,
                 max_iter=200,
                 convergence_iter=15,
                 copy=True,
                 preference=None,
                 affinity="euclidean",
                 verbose=False,
                 random_state=None,
    ):

        super().__init__()
        self.damping = damping
        self.max_iter = max_iter
        self.convergence_iter = convergence_iter
        self.copy = copy
        self.verbose = verbose
        self.preference = preference
        self.affinity = affinity
        self.random_state = random_state
        self.model = AffinityPropagation(damping = self.damping,
                                         max_iter = self.max_iter,
                                         convergence_iter = self.convergence_iter,
                                         copy = self.copy,
                                         preference=None,
                                         affinity="euclidean",
                                         verbose=False,
                                         random_state=None,

        )
        self.naming = AffinityPropagationClustering.name

    pass


class MeanShiftClustering(ClusteringWorkflowBase):
    name = "MeanShift"
    pass


class SpectralClustering(ClusteringWorkflowBase):
    name = "Spectral"
    pass


class WardHierarchicalClustering(ClusteringWorkflowBase):
    name = "WardHierarchical"
    pass


class AgglomerativeClustering(ClusteringWorkflowBase):
    name = "Agglomerative"
    pass





class OPTICSClustering(ClusteringWorkflowBase):
    name = "OPTICS"
    pass


class GaussianMixturesClustering(ClusteringWorkflowBase):
    name = "GaussianMixtures"
    pass


class BIRCHClusteringClustering(ClusteringWorkflowBase):
    name = "BIRCHClustering"
    pass


class BisectingKMeansClustering(ClusteringWorkflowBase):
    name = "BisectingKMeans"
    pass