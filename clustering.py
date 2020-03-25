#!/usr/bin/env python3

from copy import deepcopy
from typing import Tuple, List, Dict

from cluster.cluster import CustomCluster
from configurations.default_values import (
    DefaultQueries,
    DefaultShodanValues,
    DefaultValues,
)
from handlers.files_handler import FilesHandler
from handlers.shodan_handler import ShodanHandler
from helpers.tools import Tools
from parsers.http_parser import HttpParser


def get_hosts_shodan() -> Dict[str, list]:
    """
    Get hosts from Shodan for example
    @return: dict with hosts
    """
    data = ShodanHandler.get_shodan_results(
        queries_list=DefaultQueries.QUERIES,
        api_key=DefaultShodanValues.API_KEY,
        results_per_query=DefaultShodanValues.RESULTS_PER_QUERY,
    )
    FilesHandler(results=data).write_results(filename=DefaultValues.DATA_FILE)
    return data

def create_cluster(
    raw_results: Dict[str, list] = None
) -> (CustomCluster, Dict[str, list]):
    """
    Create cluster
    @return: cluster and dictionary with raw results
    """
    if not raw_results:
        raw_results = (
            FilesHandler().open_results(filename=DefaultValues.DATA_FILE)
            or get_hosts_shodan
        )
    http_parser = HttpParser(
        process_cookie=True,
        process_trash_headers=True,
        remove_digits=True,
        remove_special=True,
    )
    prepared_results = Tools.process_data(deepcopy(raw_results), http_parser)

    cluster = CustomCluster(prepared_results)
    cluster.prepare_matrix()
    # cluster.determine_k(k_range=(1, 10))
    cluster.calculate_silhouette_score()

    cluster.make_cluster()

    return cluster, raw_results


def show_example_samples(
    cluster: CustomCluster, samples_per_class: List[Tuple[str, str]]
):
    """

    @param cluster:
    @param samples_per_class:
    @return:
    """
    http_parser = HttpParser(
        process_cookie=True,
        process_trash_headers=True,
        remove_digits=True,
        remove_special=True,
    )
    print(" ---\nExamples from random choice\n --- ")
    for class_name, class_data in samples_per_class:

        processed_class_data = http_parser.process_headers(class_data)
        if not class_data:
            continue

        print(
            class_name,
            cluster.predict(processed_class_data),
            "\t - \t",
            repr(class_data),
        )


def show_example_clusters(cluster: CustomCluster, raw_results: Dict[str, list]) -> None:
    """

    @param cluster:
    @param raw_results:
    @return:
    """
    http_parser = HttpParser(
        process_cookie=True,
        process_trash_headers=True,
        remove_digits=True,
        remove_special=True,
    )
    print(" ---\nExamples from clusters directly\n --- ")
    direct_examples = {}
    for class_name, class_hosts in raw_results.items():
        for host_data in class_hosts:
            processed_host = http_parser.process_headers(host_data)
            cluster_index = cluster.predict(processed_host)[0]
            if cluster_index not in direct_examples.keys():
                direct_examples[cluster_index] = []
            else:
                direct_examples[cluster_index].append(
                    {"class_name": class_name, "data": host_data}
                )
    direct_examples = {
        key: direct_examples[key] for key in sorted(direct_examples.keys())
    }
    for index, hosts in direct_examples.items():
        print(f"Cluster [{index}]:")
        for host in hosts[:5]:
            print(
                host.get("class_name"), f"[{index}]", "\t - \t", repr(host.get("data"))
            )


if __name__ == "__main__":
    # shodan_hosts = get_hosts_shodan()
    _cluster, _raw_results = create_cluster(raw_results=None)
    _samples_per_class = Tools.get_random_samples_from_results(_raw_results)
    show_example_clusters(_cluster, _raw_results)
    # show_example_samples(_cluster, _samples_per_class)
