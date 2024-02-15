from urllib.parse import urlparse


def get_url_params(url: str) -> dict:
    params = urlparse(url)

    search_params = {}

    query_path = params.query.split("&")

    for param in query_path:
        try:
            key, value = param.split("=")
            search_params[key] = value
        except:
            continue

    return search_params


def get_url_search_params(url: str) -> dict[str, str]:
    return get_url_params(url)
