#!/usr/bin/env python3
from cluster.api.cluster_api import ClusteringAPI


class CustomConfiguration:
    HTTP_PARSER_CONFIG: dict = {
        "process_cookie": True,
        "process_trash_headers": True,
        "remove_digits": True,
        "remove_special": True,
    }


if __name__ == "__main__":
    hosts_cluster = ClusteringAPI(
        default_range=(1, 20), http_parser_config=CustomConfiguration.HTTP_PARSER_CONFIG
    )
    hosts_cluster.prepare_clusters(input_file="data/hosts_aisec.json")
    # hosts_cluster.create_plot()
    hosts_cluster.calculate_silhouette_score()
    hosts_cluster.calculate_clusters()
    hosts_cluster.predict_clusters()
    hosts_cluster.show_example_clusters()
    hosts_cluster.show_example_samples()
    hosts_cluster.save_clusters_results()
