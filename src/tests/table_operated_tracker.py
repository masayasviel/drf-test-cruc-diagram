import json
import pathlib
import re
from collections import defaultdict
from typing import Iterable

from django.urls import URLPattern, URLResolver, get_resolver

SQL_OP = re.compile(r"^\s*(?P<op>INSERT|SELECT|UPDATE|DELETE)\b", re.I)

# クエリからテーブルを拾うための正規表現
TABLE_PATTERNS = [
    re.compile(r"INSERT\s+INTO\s+([`\"']?)(?P<table>[\w\.]+)\1", re.I),
    re.compile(r"UPDATE\s+([`\"']?)(?P<table>[\w\.]+)\1", re.I),
    re.compile(r"DELETE\s+FROM\s+([`\"']?)(?P<table>[\w\.]+)\1", re.I),
    re.compile(r"FROM\s+([`\"']?)(?P<table>[\w\.]+)\1", re.I),
    re.compile(r"JOIN\s+([`\"']?)(?P<table>[\w\.]+)\1", re.I),
]

# 無視するテーブル
IGNORE_TABLES = {
    "django_migrations",
    "django_content_type",
    "django_admin_log",
    "django_session",
}


class SQLOperatedTracker:
    def __init__(self):
        self.tables_ops = defaultdict(set)  # {table: {'C','R','U','D'}}
        self.raw = []

    def __call__(self, execute, sql, params, many, context):
        try:
            self.track_sql(sql)
        except Exception:
            pass
        return execute(sql, params, many, context)

    def track_sql(self, sql: str):
        m = SQL_OP.match(sql or "")
        if not m:
            return
        crud = self.op_to_crud(m.group("op"))
        for table in set(self.extract_tables(sql)):
            self.tables_ops[table].add(crud)
            self.raw.append((crud, table, sql))

    def reset(self):
        self.tables_ops.clear()
        self.raw.clear()

    def op_to_crud(self, op: str) -> str:
        op = op.upper()
        return {"INSERT": "C", "SELECT": "R", "UPDATE": "U", "DELETE": "D"}.get(op, "?")

    def extract_tables(self, sql: str) -> Iterable[str]:
        found = []
        for pat in TABLE_PATTERNS:
            for m in pat.finditer(sql):
                t = m.group("table")
                # スキーマ付き (public.table) → テーブル名に揃える
                if "." in t:
                    t = t.split(".")[-1]
                t = t.strip("`\"'")
                if t and t not in IGNORE_TABLES:
                    found.append(t)
        return found


class EndpointCrudAggregator:
    """
    エンドポイント（METHOD + 正規化PATH）ごとにCRUD集合をマージして保持
    data: { 'GET /api/users/:id/': {table: set('C','R','U','D')} }
    """

    def __init__(self, outdir: pathlib.Path):
        self.data = defaultdict(lambda: defaultdict(set))
        self.outdir = outdir
        self.url_name_pattern_map = {}

        targets = [url for url in get_resolver().url_patterns if url.app_name not in ["admin"]]
        self.dfs_urls(targets)

    def merge(self, endpoint_key: tuple[str, str], collector: SQLOperatedTracker):
        for table, ops in collector.tables_ops.items():
            self.data[endpoint_key][table] |= ops

    def write_files(self):
        md_path = self.outdir / "md"
        json_path = self.outdir / "json"
        md_path.mkdir(parents=True, exist_ok=True)
        json_path.mkdir(parents=True, exist_ok=True)

        for ep, table_ops in sorted(self.data.items()):
            method, url_name = ep
            url_pattern = self.url_name_pattern_map.get(url_name, url_name)
            payload = {
                "method": method,
                "url_pattern": url_pattern,
                "tables": self._table_ops_to_json(table_ops),
            }
            # json
            fname = self._safe_filename(ep) + ".json"
            (json_path / fname).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            # md
            matrix = self._to_matrix(table_ops)
            endpoint = " ".join([method, url_pattern])
            content = f"# {endpoint}\n\n{matrix}\n"
            fname = self._safe_filename(ep) + ".md"
            (md_path / fname).write_text(content, encoding="utf-8")

    def _to_matrix(self, table_ops):
        header = "| Table | C | R | U | D |\n|---|:--:|:--:|:--:|:--:|"
        rows = []
        for table, ops in sorted(table_ops.items()):
            rows.append(f"| {table} | " + " | ".join("✅" if x in ops else "" for x in "CRUD") + " |")
        return "\n".join([header, *rows]) if rows else "_(no db activity)_"

    def _table_ops_to_json(self, table_ops: dict[str, set[str]]) -> dict:
        out = {}
        for table in sorted(table_ops.keys()):
            ops = table_ops[table]
            out[table] = {k: (k in ops) for k in ["C", "R", "U", "D"]}
        return out

    def _safe_filename(self, ep_key: tuple[str, str]) -> str:
        s = " ".join(ep_key)
        return re.sub(r"[^A-Za-z0-9_.-]+", "_", s)[:200]

    def dfs_urls(self, url_patterns, prefix=""):
        for url in url_patterns:
            if isinstance(url, URLResolver):
                # ネストしたResolverのprefixも含める
                self.dfs_urls(url.url_patterns, prefix + str(url.pattern))
            elif isinstance(url, URLPattern):
                if url.name:  # 名前付きのものだけ
                    self.url_name_pattern_map[url.name] = prefix + str(url.pattern)
