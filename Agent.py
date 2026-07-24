import os
from kaizen.core.modules.backend import ServiceClass
from kaizen.core.modules.Schemas import SearchResult
from kaizen.core.modules.utils import ripgrep


class SearchEngine(ServiceClass):
    def __init__(self):
        pass

    def invoke(self, search_queries: list[str], workspace: str = None) -> list[SearchResult]:
        if workspace is None:
            workspace = os.getcwd()
        result = []

        for query in search_queries:
            matches = ripgrep(query, workspace)
            if isinstance(matches, dict) and "error" in matches:
                continue
            for match in matches:
                if not match.get("file") or not match.get("line"):
                    continue
                result.append(
                    SearchResult(
                        path=match["file"],
                        line=match["line"],
                        preview=match["text"],
                    )
                )

        return result


if __name__ == "__main__":
    result = SearchEngine()
    print(result.invoke(["tool", "planner"]))
