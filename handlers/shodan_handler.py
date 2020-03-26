#!/usr/bin/env python3

from itertools import islice
from typing import List, Dict

from shodan import Shodan, APIError

from configurations.default_values import DefaultShodanValues, DefaultQueries


class ShodanHandler:
    def __init__(self, api_key: str = DefaultShodanValues.API_KEY):
        self.api_key = api_key

    def get_shodan_results(
        self,
        queries_list: List[str] = None,
        results_per_query: int = DefaultShodanValues.RESULTS_PER_QUERY,
    ) -> Dict[str, list]:
        """
        Get some hosts from Shodan
        @param queries_list: list of queries
        @param results_per_query: how many results do we need per query
        @return: dictionary {"product": ["list", "of", "hosts"]}
        """
        if queries_list is None:
            queries_list = DefaultQueries.QUERIES
        results = dict()
        for query in queries_list:
            print(f"Get results for {query}")
            try:
                results_generator = Shodan(self.api_key).search_cursor(
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
