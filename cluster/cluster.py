from typing import Dict, Tuple

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

from configurations.default_values import AdditionalStopWords


class CustomCluster:
    def __init__(self, input_data: Dict[str, list] = None):
        self.input_data = input_data
        self.matrix: text.TfidfTransformer.transform or None = None
        self.vectorizer: text.TfidfVectorizer or None = None
        self.model: KMeans or None = None
        self.best_k: int = 1

    def set_input_data(self, input_data: Dict[str, list]) -> None:
        """
        Set or update the input data which is cluster based on
        @param input_data: input data to clusterize
        @return: None
        """
        self.input_data = input_data

    def prepare_matrix(self) -> None:
        """
        Prepare the matrix
        @return: None
        """
        flat_response_list = [
            response
            for list_of_responses in self.input_data.values()
            for response in list_of_responses
        ]
        self.vectorizer = TfidfVectorizer(
            stop_words=text.ENGLISH_STOP_WORDS.union(AdditionalStopWords.WORDS)
        )
        self.matrix = self.vectorizer.fit_transform(flat_response_list)

    def calculate_silhouette_score(self, best_score: int = -1, k_range: Tuple[int, int] = (2, 20)) -> int:
        """
        Calculate the best number of clusters via Silhouette score method
        @param best_score: best score to start from
        @param k_range: possible range of cluster numbers
        @return: best quantity of clusters
        """
        if k_range[0] < 2:
            _temp_k_range = list(k_range)
            _temp_k_range[0] = 2
            k_range = tuple(_temp_k_range)
        for k in range(*k_range):
            model = KMeans(n_clusters=k, init="k-means++", max_iter=500, n_init=100, n_jobs=-1, algorithm="full")
            model.fit(self.matrix)
            labels = model.predict(self.matrix)
            score = silhouette_score(model.transform(self.matrix), labels)

            print(f"Current cluster: {k}, silhouette score: {score}")
            if score > best_score:
                self.best_k = k
                best_score = score
        print(f"The best K number is: {self.best_k}")
        return self.best_k

    def determine_k(self, k_range: Tuple[int, int] = (1, 10)) -> plt.show:
        """
        Determine k with the Elbow method
        @return: plot image
        """
        cost = []
        for i in range(*k_range):
            print(f"Calculate results for {i} clusters")
            model = KMeans(n_clusters=i, init="k-means++", max_iter=500, n_init=100, n_jobs=-1)
            model.fit(self.matrix)
            cost.append(model.inertia_)

        plt.plot(range(*k_range), cost, color="g", linewidth="0.5")
        plt.show()

    def make_cluster(self, display_limit: int = 20, clusters_q: int = None) -> None:
        """
        Clusterize all of the results
        @return: None
        """
        if clusters_q is None:
            clusters_q = self.best_k or 3
        self.model = KMeans(
            n_clusters=clusters_q, init="k-means++", max_iter=500, n_init=100, n_jobs=-1
        )
        self.model.fit(self.matrix)

        order_centroids = self.model.cluster_centers_.argsort()[:, ::-1]
        terms = self.vectorizer.get_feature_names()
        for cluster_index in range(clusters_q):
            print(f"Current cluster: {cluster_index}")
            print(
                [
                    terms[index]
                    for index in order_centroids[cluster_index, :display_limit]
                ]
            )

    def predict(self, element_to_predict: str) -> KMeans.predict:
        """
        Predict that host is belong to some cluster
        @return: index of matched cluster
        """
        alpha = self.vectorizer.transform([element_to_predict])
        return self.model.predict(alpha)
