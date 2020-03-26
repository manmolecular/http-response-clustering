#!/usr/bin/env python3

from copy import deepcopy
from typing import Tuple, List, Dict

from cluster.core.cluster import CustomCluster
from cluster.configurations.default_values import DefaultValues
from cluster.handlers.files_handler import FilesHandler
from cluster.handlers.shodan_handler import ShodanHandler
from cluster.helpers.tools import Tools
from cluster.parsers.http_parser import HttpParser


class BasicConfiguration:
    HTTP_PARSER_CONFIG: dict = {
        "process_cookie": True,
        "process_trash_headers": True,
        "remove_digits": True,
        "remove_special": True,
    }


class ClusteringAPI:
    def __init__(
        self,
        http_parser_config: Dict[str, bool] or None = None,
        raw_results: Dict[str, list or str] or None = None,
        results_per_cluster: Dict[int, list] or None = None,
        shodan_handler: ShodanHandler = ShodanHandler(),
        files_handler: FilesHandler = FilesHandler(),
        cluster: CustomCluster = CustomCluster(),
        default_range: Tuple[int, int] = (1, 20),
    ):
        # Obtain the basic configuration for the HTTP Parser
        if http_parser_config is None:
            http_parser_config = BasicConfiguration.HTTP_PARSER_CONFIG

        # Public values
        self.results_per_cluster = results_per_cluster
        self.cluster = cluster
        self.default_range = default_range

        # Semi-private values
        self._http_parser = HttpParser(**http_parser_config)
        self._raw_results = raw_results
        self._shodan_handler = shodan_handler
        self._files_handler = files_handler
        self._best_k: int or None = None

    def get_hosts_shodan(self) -> Dict[str, list]:
        """
        Get hosts from the Shodan, in case if we need some
        raw data for the 'in the wild' cases testing
        @return: Dictionary with dork as a host-class
        name and related hosts to it
        """
        data = self._shodan_handler.get_shodan_results()
        self._files_handler.write_json_file(filename=DefaultValues.DATA_FILE, data=data)
        return data

    def prepare_clusters(
        self, input_file: str = None, raw_results: Dict[str, list] = None
    ) -> None:
        """
        Prepare cluster - preprocess and prepare the data, matrix, fit transformations, etc.
        @param input_file: filename to open and analyse, for example, data from ./data/*.json
        @param raw_results: raw results (can be imported from other Shodan, Censys handlers, etc.)
        @return: None
        """
        if raw_results is not None:
            self._raw_results = raw_results
        elif self._raw_results is None:
            self._raw_results = self._files_handler.open_json_file(
                filename=input_file or DefaultValues.DATA_FILE
            )
        else:
            self._raw_results = self.get_hosts_shodan()

        prepared_results = Tools.process_data(
            deepcopy(self._raw_results), self._http_parser
        )

        # Prepare data
        self.cluster.set_input_data(prepared_results)
        self.cluster.prepare_matrix()

    def set_default_range(self, default_range: Tuple[int, int]) -> None:
        """
        Set the default range for analysis clusters "from" -> "to"
        @param default_range: Tuple representation of range, num to num
        @return: None
        """
        self.default_range = default_range

    def calculate_silhouette_score(
        self, k_range: Tuple[int, int] or None = None
    ) -> None:
        """
        Analyse and determine the best number of clusters with
        the Silhouette score method
        @param k_range: redefine default range, see 'set_default_range' function
        @return: None
        """
        self._best_k = self.cluster.calculate_silhouette_score(
            k_range=k_range or self.default_range
        )

    def create_plot(self) -> None:
        """
        Create the Elbow method plots to check our Silhouette score
        predictions (in case if it wrong somehow)
        @return: None
        """
        self.cluster.determine_k(k_range=self.default_range)

    def calculate_clusters(self, best_k: int or None = None) -> None:
        """
        Calculate the final clusters, based on the best K number of clusters,
        obtained with the Elbow method or with the Silhouette score method
        @param best_k: best number of clusters based on the Silhouette score, for example
        @return: None
        """
        self.cluster.make_clusters(clusters_q=best_k or self._best_k)

    def predict_clusters(self, raw_results: Dict[str, list] = None) -> Dict[int, list]:
        """
        Sort out hosts to different matching clusters
        @param raw_results: raw input results to sort
        @return: dictionary with results per cluster
        """
        if raw_results is None:
            raw_results = self._raw_results
        results_per_cluster = {}
        for class_name, class_hosts in raw_results.items():
            for host_data in class_hosts:
                processed_host = self._http_parser.process_headers(host_data)
                cluster_index = self.cluster.predict(processed_host)[0]
                if cluster_index not in results_per_cluster.keys():
                    results_per_cluster[cluster_index] = []
                else:
                    results_per_cluster[cluster_index].append(
                        {"class_name": class_name, "data": host_data}
                    )
        self.results_per_cluster = results_per_cluster
        return results_per_cluster

    def show_example_clusters(
        self, results_per_cluster: Dict[int, list] or None = None
    ) -> None:
        """
        Show basic examples of clustering: hosts per clusters
        @param results_per_cluster: groups of hosts per cluster
        @return: None
        """
        if results_per_cluster is None:
            results_per_cluster = self.results_per_cluster or self.predict_clusters()
        results_per_cluster = {
            key: results_per_cluster[key] for key in sorted(results_per_cluster.keys())
        }
        print(" ---\nExamples from clusters directly\n --- ")
        for index, hosts in results_per_cluster.items():
            print(f"Cluster [{index}]:")
            for host in hosts[:5]:
                print(
                    host.get("class_name"),
                    f"[{index}]",
                    "\t - \t",
                    repr(host.get("data")),
                )

    def show_example_samples(
        self, samples_per_class: List[Tuple[str, str]] or None = None
    ) -> None:
        """
        Show random examples
        @param samples_per_class: small groups of random samples from results
        @return: None
        """
        if samples_per_class is None:
            samples_per_class = Tools.get_random_samples_from_results(self._raw_results)
        print(" ---\nExamples from random choice\n --- ")
        for class_name, class_data in samples_per_class:
            processed_class_data = self._http_parser.process_headers(class_data)
            if not class_data:
                continue
            print(
                class_name,
                self.cluster.predict(processed_class_data),
                "\t - \t",
                repr(class_data),
            )

    def save_clusters_results(
        self, results_per_cluster: Dict[int, list] or None = None
    ) -> None:
        """
        Save results from every cluster in separate JSON file
        @param results_per_cluster: groups of hosts per cluster
        @return: None
        """
        if results_per_cluster is None:
            results_per_cluster = self.results_per_cluster or self.predict_clusters()
        self._files_handler.update_save_time()
        q_len = len(results_per_cluster.keys())
        for index, hosts in results_per_cluster.items():
            self._files_handler.write_json_file(
                filename=f"cluster_{index}.json", data=hosts, q_clusters=q_len
            )
