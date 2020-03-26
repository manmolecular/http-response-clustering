#!/usr/bin/env python3


class DefaultShodanValues:
    """
    Define default Shodan values
    """

    API_KEY: str = ""
    RESULTS_PER_QUERY: int = 1000


class DefaultPlates:
    """
    Default plates values
    """

    COOKIE_REPLACER: str = "cookie_value"
    RANDOM_REPLACER: str = "random_value_"


class DefaultValues:
    """
    Define default values
    """

    DATA_FILE: str = "data/hosts_servers.json"


class DefaultQueries:
    """
    Define default queries to scan with Shodan
    """

    QUERIES: list = [
        "kibana content-length: 217",
        'http.title:"MLflow"',
        'http.title:"Kubeflow Central Dashboard"',
    ]


class TrashHeaders:
    """
    Define headers that should be replaced from headers analysis
    """

    HEADERS: list = [
        "Expires",
        "Date",
        "Last-Modified",
        "ETag",
        "Content-Length",
    ]  # + ["Server"]


class AdditionalStopWords:
    """
    Exclude some words from analyzing.

    Extend with ["apache", "nginx", "flask"] to check in more real-life cases
    """

    # fmt: off
    WORDS: list = ["connection", "length", "http", "html"] + [""]
    # fmt: on
