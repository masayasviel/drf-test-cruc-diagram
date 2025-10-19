import json
import pathlib

from django.urls import URLPattern, URLResolver, get_resolver
import sql_metadata


class QueryLogger:
    def __init__(self):
        self.queries = []

    def __call__(self, execute, sql, params, many, context):
        self.queries.append(sql)
        return execute(sql, params, many, context)
    
    def reset(self):
        self.queries.clear()


class Aggregator:
    def __init__(self, outdir: pathlib.Path):
        self.data: dict[tuple[str, str], set[str]] = {}
        self.outdir = outdir
        self.url_name_pattern_map = {}

        targets = [url for url in get_resolver().url_patterns if url.app_name not in ["admin"]]
        self.dfs_urls(targets)

    def merge(self, endpoint_key: tuple[str, str], ql: QueryLogger):
        for query in ql.queries:
            parser = sql_metadata.Parser(query)
            self.data.setdefault(endpoint_key, set()).update(set(parser.tables))

    def write_file(self):
        self.outdir.mkdir(parents=True, exist_ok=True)
        result = []
        for ep, table_ops in sorted(self.data.items()):
            method, url_name = ep
            url_pattern = self.url_name_pattern_map.get(url_name, url_name)
            result.append({
                "method": method,
                "url_pattern": url_pattern,
                "tables": list(table_ops),
            })
        with open(self.outdir / 'data.json', 'w') as f:
            f.write(json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            ))

    def dfs_urls(self, url_patterns, prefix=""):
        for url in url_patterns:
            if isinstance(url, URLResolver):
                # ネストしたResolverのprefixも含める
                self.dfs_urls(url.url_patterns, prefix + str(url.pattern))
            elif isinstance(url, URLPattern):
                if url.name:  # 名前付きのものだけ
                    self.url_name_pattern_map[url.name] = prefix + str(url.pattern)
