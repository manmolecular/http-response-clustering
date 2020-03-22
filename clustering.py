#!/usr/bin/env python3

from handlers.files_handler import FilesHandler
from handlers.shodan_handler import ShodanHandler
from helpers.tools import Tools
from parsers.http_parser import HttpParser
from copy import deepcopy
from cluster.cluster import CustomCluster
from typing import Tuple, List, Dict


def get_hosts_shodan() -> Dict[str, list]:
    """
    Get hosts from Shodan for example
    @return: dict with hosts
    """
    queries_list = [
        'kibana content-length: 217',
        'http.title:"MLflow"',
        'http.title:"Kubeflow Central Dashboard"',
    ]
    data = ShodanHandler.get_shodan_results(queries_list=queries_list,
                                            api_key="",
                                            results_per_query=1000)
    FilesHandler(results=data).write_results()
    return data


def create_cluster(raw_results: Dict[str, list] = None) -> (CustomCluster, Dict[str, list]):
    """
    Create cluster
    @return: cluster and dictionary with raw results
    """
    if not raw_results:
        raw_results = FilesHandler().open_results() or get_hosts_shodan
    http_parser = HttpParser(process_cookie=False,
                             process_trash_headers=False,
                             remove_digits=False,
                             remove_special=False)
    prepared_results = Tools.process_data(deepcopy(raw_results), http_parser)

    cluster = CustomCluster(prepared_results)
    cluster.prepare_matrix()
    cluster.determine_k()

    # User value from determine_k plot here
    cluster.make_cluster(clusters_q=3)

    return cluster, raw_results


def show_examples(cluster: CustomCluster, samples_per_class: List[Tuple[str, str]]) -> None:
    """

    @param cluster:
    @param samples_per_class:
    @return:
    """
    http_parser = HttpParser()
    print(" ---\nExamples\n ---")
    for class_name, class_data in samples_per_class:

        class_data = http_parser.process_headers(class_data)
        if not class_data:
            continue

        print(class_name, cluster.predict(class_data), "\t - \t", repr(class_data))


if __name__ == "__main__":
    # shodan_hosts = get_hosts_shodan()
    _cluster, _raw_results = create_cluster(raw_results=None)
    _samples_per_class = Tools.get_random_samples_from_results(_raw_results)
    show_examples(_cluster, _samples_per_class)

