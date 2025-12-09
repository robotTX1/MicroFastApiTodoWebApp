from yarl import URL

from microfastapitodowebapp.domain.query import TodoQuery, QueryMode


def build_url(base_url: str, query: TodoQuery, query_mode: QueryMode, extra: dict[str, str] = None) -> str:
    query_params = query.to_dict()
    query_params["mode"] = query_mode.value
    if "search" in query_params:
        query_params["search"] = build_search_query(query_params["search"])
    if extra:
        for key, value in extra.items():
            query_params[key] = value
    url = URL.build(path=base_url, query=query_params)
    return str(url)

def build_search_query(search: str) -> str | None:
    if is_not_blank(search):
        return f"title=ilike='{search}' or description=ilike='{search}' or categories.name=ilike='{search}'"
    return None

def is_not_blank(string: str) -> bool:
    return bool(string and string.strip())