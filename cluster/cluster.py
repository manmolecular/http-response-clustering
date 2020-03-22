from typing import Dict, Tuple

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer
from configurations.default_values import AdditionalStopWords


class CustomCluster:
    def __init__(self, input_data: Dict[str, list]):
        self.input_data = input_data
        self.matrix: text.TfidfTransformer.transform or None = None
        self.vectorizer: text.TfidfVectorizer or None = None
        self.model: KMeans or None = None

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

    def determine_k(self, k_range: Tuple[int, int] = (1, 10)) -> plt.show:
        """
        Determine k with the Elbow method
        @return: plot image
        """
        cost = []
        for i in range(*k_range):
            print(f"Calculate results for {i} clusters")
            model = KMeans(n_clusters=i, init="k-means++", max_iter=500, n_init=100)
            model.fit(self.matrix)
            cost.append(model.inertia_)

        plt.plot(range(*k_range), cost, color='g', linewidth='0.5')
        plt.show()

    def make_cluster(self, display_limit: int = 20, clusters_q: int = 3,) -> None:
        """
        Clusterize all of the results
        @return: None
        """

        self.model = KMeans(n_clusters=clusters_q, init="k-means++", max_iter=500, n_init=100)
        self.model.fit(self.matrix)

        order_centroids = self.model.cluster_centers_.argsort()[:, ::-1]
        terms = self.vectorizer.get_feature_names()
        for cluster_index in range(clusters_q):
            print(f"Current cluster: {cluster_index}")
            print(
                [terms[index] for index in order_centroids[cluster_index, :display_limit]]
            )

    def predict(self, element_to_predict: str) -> KMeans.predict:
        """
        Predict that host is belong to some cluster
        @return: index of matched cluster
        """
        alpha = self.vectorizer.transform([element_to_predict])
        return self.model.predict(alpha)
