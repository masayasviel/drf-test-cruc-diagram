import json
import pathlib


class QueryLogger:
    def __init__(self):
        self.queries = []

    def __call__(self, execute, sql, params, many, context):
        current_query = {"sql": sql, "params": params, "many": many}
        self.queries.append(current_query)
        return execute(sql, params, many, context)
    
    def reset(self):
        self.queries.clear()


class Aggregator:
    def __init__(self, outdir: pathlib.Path):
        self.data = []
        self.outdir = outdir

    def merge(self, endpoint_key: tuple[str, str], ql: QueryLogger):
        self.data.append({
            'method': endpoint_key[0],
            'path': endpoint_key[1],
            'data': ql.queries,
        })

    def write_file(self):
        with open(self.outdir / 'data.json', 'w') as f:
            f.write(json.dumps(
                self.data,
                indent=2,
                ensure_ascii=False,
            ))
