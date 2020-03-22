#!/usr/bin/env python3
from typing import Dict, List, Tuple
from parsers.http_parser import HttpParser
from random import sample


class Tools:
    def __init__(self):
        pass

    @staticmethod
    def process_data(
        results_to_process: Dict[str, list], http_parser: HttpParser = HttpParser()
    ) -> Dict[str, list]:
        """
        Process all of the results, retrieve some headers
        @param results_to_process: results to process
        @param http_parser: parser with configuration
        @return: dictionary with products and hosts
        """
        for product, hosts in results_to_process.items():
            for index, element in enumerate(hosts):
                processed_headers = http_parser.process_headers(element)
                if not processed_headers:
                    results_to_process[product][index] = ""
                    continue
                results_to_process[product][index] = processed_headers
            results_to_process[product] = [host for host in hosts if host]
        return results_to_process

    @staticmethod
    def get_random_samples_from_results(
        _results: Dict[str, list], samples_q: int = 10
    ) -> List[Tuple[str, str]]:
        """
        Get some random samples to check predictions
        @param _results: results to get samples from
        @param samples_q: quantity of random samples
        @return: samples in a list
        """
        return [
            (_class_name, _element)
            for _class_name, _class_list in _results.items()
            for _element in sample(_class_list, samples_q)
        ]
