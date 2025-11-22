from yarl import URL

from microfastapitodowebapp.domain.query import TodoQuery, QueryMode


def build_url(base_url: str, query: TodoQuery, query_mode: QueryMode, extra: dict[str, str] = None) -> str:
    query_params = query.to_dict()
    query_params["mode"] = query_mode.value
    if extra:
        for key, value in extra.items():
            query_params[key] = value
    url = URL.build(path=base_url, query=query_params)
    return str(url)
