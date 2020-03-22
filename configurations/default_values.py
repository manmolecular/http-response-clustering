#!/usr/bin/env python3


class DefaultShodanValues:
    """
    Define default Shodan values
    """

    API_KEY: str = ""
    RESULTS_PER_QUERY: int = 1000


class DefaultValues:
    """
    Define default values
    """

    DATA_FILE: str = "data/hosts_aisec.json"


class DefaultQueries:
    """
    Define default queries to scan with Shodan
    """

    QUERIES: list = ["Apache", "Nginx", "Flask"]


class TrashHeaders:
    """
    Define headers that should be skipped from headers analysis
    """

    HEADERS: list = ["Expires", "Date", "Last-Modified", "ETag", "Content-Length"]  # + ["Server"]


class AdditionalStopWords:
    """
    Exclude some words from analyzing.

    Extend with ["apache", "nginx", "flask"] to check in more real-life cases
    """

    # fmt: off
    WORDS: list = ["connection", "length", "http", "html"] + [""]
    # fmt: on
