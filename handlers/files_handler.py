#!/usr/bin/env python3

from json import dump, load
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from configurations.default_values import DefaultValues as FilesDefaultValues


class FilesHandler:
    def __init__(
        self,
        filename: str = FilesDefaultValues.DATA_FILE,
        data: Dict[str, str] or None = None,
    ):
        self.filename = filename
        self.data = data
        self.save_time = self.update_save_time()

    def open_json_file(self, filename: str or None = None) -> Dict[str, list or str]:
        """
        Open some previous results of scanning to process and clusterize it
        @param filename: name of file to open
        @return: loaded JSON data from file
        """
        with open(file=filename or self.filename, mode="r") as input_data:
            return load(fp=input_data)

    def update_save_time(self) -> str:
        """
        Return current time
        @return: current time
        """
        save_time = datetime.now().strftime("d%d-%M-%Y_t%H-%M-%S")
        self.save_time = save_time
        return save_time

    def write_json_file(self, filename: str or None = None, data: Any = None, q_clusters: int or str = "unknown") -> None:
        """
        Write results to JSON file
        @param filename: filename of file to write data into
        @param data: data to write
        @param q_clusters: quantity of clusters
        @return: None
        """
        path = Path(f"results/{q_clusters}_clusters_{self.save_time}/{filename or self.filename}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(file=path, mode="w") as output_file:
            dump(obj=data or self.data, fp=output_file, indent=4)
