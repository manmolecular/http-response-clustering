#!/usr/bin/env python3

from copy import deepcopy
from typing import Tuple, List, Dict

from cluster.cluster import CustomCluster
from configurations.default_values import DefaultValues
from handlers.files_handler import FilesHandler
from handlers.shodan_handler import ShodanHandler
from helpers.tools import Tools
from parsers.http_parser import HttpParser


class BasicConfiguration:
    HTTP_PARSER_CONFIG: dict = {
        "process_cookie": True,
        "process_trash_headers": True,
        "remove_digits": True,
        "remove_special": True
    }


class ClusteringAPI:
    def __init__(self,
                 http_parser: HttpParser = HttpParser(**BasicConfiguration.HTTP_PARSER_CONFIG),
                 raw_results: Dict[str, list or str] or None = None,
                 results_per_cluster: Dict[int, list] or None = None,
                 shodan_handler: ShodanHandler = ShodanHandler(),
                 files_handler: FilesHandler = FilesHandler(),
                 cluster: CustomCluster = CustomCluster(),
                 default_range: Tuple[int, int] = (1, 20)):
        self.http_parser = http_parser
        self.raw_results = raw_results
        self.results_per_cluster = results_per_cluster
        self.shodan_handler = shodan_handler
        self.files_handler = files_handler
        self.cluster = cluster
        self.default_range = default_range

    def get_hosts_shodan(self) -> Dict[str, list]:
        """
        Get hosts from Shodan for example
        @return: dict with hosts
        """
        data = self.shodan_handler.get_shodan_results()
        self.files_handler.write_json_file(filename=DefaultValues.DATA_FILE, data=data)
        return data

    def create_cluster(
        self, raw_results: Dict[str, list] = None
    ) -> None:
        """
        Create cluster - prepare the data, determine K number of clusters
        and calculate Silhouette score to check predictions.
        @return: None
        """
        if raw_results is not None:
            self.raw_results = raw_results
        elif self.raw_results is None:
            self.raw_results = self.files_handler.open_json_file(filename=DefaultValues.DATA_FILE)
        else:
            self.raw_results = self.get_hosts_shodan()

        prepared_results = Tools.process_data(deepcopy(self.raw_results), self.http_parser)

        # Prepare data
        self.cluster.set_input_data(prepared_results)
        self.cluster.prepare_matrix()

        # Analyse and determine the best K number in range from 1 to 20
        best_k = self.cluster.calculate_silhouette_score(k_range=self.default_range)

        # Create final clusters with the best K number
        self.cluster.make_cluster(clusters_q=best_k)

    def create_plots(self) -> None:
        """
        Create plots with the Elbow method
        @return: None
        """
        self.cluster.determine_k(k_range=self.default_range)

    def prepare_output_clusters(self, raw_results: Dict[str, list] = None) -> Dict[int, list]:
        """

        @param raw_results:
        @return:
        """
        if raw_results is None:
            raw_results = self.raw_results
        results_per_cluster = {}
        for class_name, class_hosts in raw_results.items():
            for host_data in class_hosts:
                processed_host = self.http_parser.process_headers(host_data)
                cluster_index = self.cluster.predict(processed_host)[0]
                if cluster_index not in results_per_cluster.keys():
                    results_per_cluster[cluster_index] = []
                else:
                    results_per_cluster[cluster_index].append(
                        {"class_name": class_name, "data": host_data}
                    )
        self.results_per_cluster = results_per_cluster
        return results_per_cluster

    def show_example_clusters(self, results_per_cluster: Dict[int, list] or None = None) -> None:
        """

        @param results_per_cluster:
        @return:
        """
        if results_per_cluster is None:
            results_per_cluster = self.results_per_cluster or self.prepare_output_clusters()
        results_per_cluster = {
            key: results_per_cluster[key] for key in sorted(results_per_cluster.keys())
        }
        print(" ---\nExamples from clusters directly\n --- ")
        for index, hosts in results_per_cluster.items():
            print(f"Cluster [{index}]:")
            for host in hosts[:5]:
                print(
                    host.get("class_name"), f"[{index}]", "\t - \t", repr(host.get("data"))
                )

    def show_example_samples(
        self, samples_per_class: List[Tuple[str, str]] or None = None
    ):
        """

        @param samples_per_class:
        @return:
        """
        if samples_per_class is None:
            samples_per_class = Tools.get_random_samples_from_results(self.raw_results)
        print(" ---\nExamples from random choice\n --- ")
        for class_name, class_data in samples_per_class:
            processed_class_data = self.http_parser.process_headers(class_data)
            if not class_data:
                continue
            print(
                class_name,
                self.cluster.predict(processed_class_data),
                "\t - \t",
                repr(class_data),
            )

    def save_cluster_results(self, results_per_cluster: Dict[int, list] or None = None) -> None:
        """

        @param results_per_cluster:
        @return:
        """
        if results_per_cluster is None:
            results_per_cluster = self.results_per_cluster or self.prepare_output_clusters()
        self.files_handler.update_save_time()
        q_len = len(results_per_cluster.keys())
        for index, hosts in results_per_cluster.items():
            self.files_handler.write_json_file(filename=f"cluster_{index}.json", data=hosts, q_clusters=q_len)


if __name__ == "__main__":
    hosts_cluster = ClusteringAPI(default_range=(1, 20))
    hosts_cluster.create_cluster()
    hosts_cluster.prepare_output_clusters()
    hosts_cluster.show_example_clusters()
    hosts_cluster.show_example_samples()
    hosts_cluster.save_cluster_results()
