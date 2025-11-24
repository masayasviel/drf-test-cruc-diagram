import json
import pathlib
from collections import defaultdict

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


class ExtractTableOperate:
    CRUD_CREATE = "C"
    CRUD_READ = "R"
    CRUD_UPDATE = "U"
    CRUD_DELETE = "D"

    def __init__(self):
        self._crud_map: dict[str, set[str]] = defaultdict(set)
        self._cte_names: set[str] = set()

    def extract(self, query: str):
        self._reset_props()

        ast = sqlglot.parse_one(query, read="mysql")
        self._aggregate_cte_names(ast)

        if isinstance(ast, exp.Insert):
            self._handle_insert(ast)
        elif isinstance(ast, exp.Update):
            self._handle_update(ast)
        elif isinstance(ast, exp.Delete):
            self._handle_delete(ast)
        elif isinstance(ast, exp.Select):
            self._handle_select(ast)

        return self._crud_map

    def _reset_props(self):
        self._crud_map = defaultdict(set)
        self._cte_names = set()

    def _aggregate_cte_names(self, root_expr: exp.Expression) -> None:
        for with_expr in root_expr.find_all(exp.With):
            for cte in with_expr.expressions:
                if alias := cte.alias:
                    self._cte_names.add(alias)

    def _mark_read_tables(
        self,
        expr: exp.Expression,
    ):
        for table in expr.find_all(exp.Table):
            name = table.name
            if not name:
                continue
            # CTE名を除去
            if name in self._cte_names:
                continue
            self._crud_map[name].add(self.CRUD_READ)

    def _handle_select(self, stmt: exp.Select):
        self._mark_read_tables(stmt)

    def _handle_insert(self, stmt: exp.Insert):
        target = stmt.this
        if isinstance(target, exp.Schema):
            target = target.this

        if isinstance(target, exp.Table):
            name = target.name
            if name and name not in self._cte_names:
                self._crud_map[name].add(self.CRUD_CREATE)

        # INSERT INTO ... SELECT ... のREAD部分
        if stmt.expression is not None:
            self._handle_select(stmt.expression)

    def _handle_update(self, stmt: exp.Update):
        target = stmt.this
        if isinstance(target, exp.Table):
            name = target.name
            if name and name not in self._cte_names:
                self._crud_map[name].add(self.CRUD_UPDATE)

        self._mark_read_tables(stmt)

    def _handle_delete(self, stmt: exp.Delete):
        target = stmt.this
        if isinstance(target, exp.Table):
            name = target.name
            if name and name not in self._cte_names:
                self._crud_map[name].add(self.CRUD_DELETE)

        self._mark_read_tables(stmt)


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
