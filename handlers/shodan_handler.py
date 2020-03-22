#!/usr/bin/env python3

from itertools import islice
from shodan import Shodan, APIError
from configurations.default_values import DefaultShodanValues
from typing import List, Dict


class ShodanHandler:
    def __init__(self):
        pass

    @staticmethod
    def get_shodan_results(
        queries_list: List[str],
        api_key: str = DefaultShodanValues.API_KEY,
        results_per_query: int = DefaultShodanValues.RESULTS_PER_QUERY,
    ) -> Dict[str, list]:
        """
        Get some hosts from Shodan
        @param queries_list: list of queries
        @param api_key: Shodan API key
        @param results_per_query: how many results do we need per query
        @return: dictionary {"product": ["list", "of", "hosts"]}
        """
        results = dict()
        for query in queries_list:
            print(f"Get results for {query}")
            try:
                results_generator = Shodan(api_key).search_cursor(
                    query=query, minify=True
                )
            except APIError as shodan_err:
                print(f"Shodan search error, {shodan_err.value}")
                continue
            limited_results = islice(results_generator, results_per_query)
            results.update(
                {
                    query: [
                        host.get("data") for host in limited_results if host.get("data")
                    ]
                }
            )
        return results
