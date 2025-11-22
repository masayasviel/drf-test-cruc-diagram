import json
import pathlib

import sqlglot
from django.conf import settings
from django.urls import URLPattern, URLResolver, get_resolver
from sqlglot import exp


class QueryLogger:
    EXCLUDED_PREFIXES = ("BEGIN", "SAVEPOINT", "RELEASE SAVEPOINT", "ROLLBACK TO SAVEPOINT", "COMMIT")

    def __init__(self):
        self.queries = []

    def __call__(self, execute, sql, params, many, context):
        if sql.strip().upper().startswith(self.EXCLUDED_PREFIXES):
            return execute(sql, params, many, context)

        format_query = sql
        if params:
            format_query = sql % tuple(repr(p) for p in params)
        self.queries.append(format_query)

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
            ast = sqlglot.parse_one(query, read=settings.DB_ENGINE)
            self.data.setdefault(endpoint_key, set()).update({table.name for table in ast.find_all(exp.Table)})

    def write_file(self):
        self.outdir.mkdir(parents=True, exist_ok=True)
        result = []
        for ep, table_ops in sorted(self.data.items()):
            method, url_name = ep
            url_pattern = self.url_name_pattern_map.get(url_name, url_name)
            result.append(
                {
                    "method": method,
                    "url_pattern": url_pattern,
                    "tables": list(table_ops),
                }
            )
        with open(self.outdir / "data.json", "w") as f:
            f.write(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False,
                )
            )

    def dfs_urls(self, url_patterns, prefix=""):
        for url in url_patterns:
            if isinstance(url, URLResolver):
                # ネストしたResolverのprefixも含める
                self.dfs_urls(url.url_patterns, prefix + str(url.pattern))
            elif isinstance(url, URLPattern):
                if url.name:  # 名前付きのものだけ
                    self.url_name_pattern_map[url.name] = prefix + str(url.pattern)
