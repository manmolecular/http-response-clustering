#!/usr/bin/env python3

from configurations.default_values import DefaultValues as FilesDefaultValues
from typing import Dict
from json import dump, load


class FilesHandler:
    def __init__(self, filename: str = FilesDefaultValues.DATA_FILE, results: Dict[str, str] or None = None):
        self.filename = filename
        self.results = results

    def open_results(self, filename: str or None = None) -> Dict[str, list or str]:
        """
        Open previous results of scanning to process and clusterize it
        @param filename: name of file to open
        @return: loaded JSON data from file
        """
        with open(file=filename or self.filename, mode="r") as input_data:
            return load(fp=input_data)

    def write_results(self, filename: str or None = None) -> None:
        """
        Write results to JSON file
        @param filename: filename of file to write data into
        @return: None
        """
        with open(file=filename or self.filename, mode="w") as output_file:
            dump(obj=self.results, fp=output_file)
