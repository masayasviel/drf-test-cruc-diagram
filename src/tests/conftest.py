import pathlib
import shutil

import pytest
from django.db import connection
from django.urls import Resolver404, resolve
from rest_framework.test import APIClient

from .query_logger import Aggregator, QueryLogger

HERE = pathlib.Path(__file__).parent


@pytest.fixture(scope="session", autouse=True)
def write_endpoint_reports_after_session(request):
    outdir = HERE / "docs"
    shutil.rmtree(outdir)
    aggregator = Aggregator(outdir=outdir)
    request.config._aggregator = aggregator
    yield
    aggregator.write_file()


@pytest.fixture(autouse=True)
def collect_crud_by_endpoint(request, monkeypatch):
    aggregator: Aggregator = request.config._aggregator
    ql = QueryLogger()
    orig_generic = APIClient.generic

    def endpoint_key_from(method: str, path: str) -> tuple[str, str]:
        try:
            m = resolve(path)
            return (method, m.url_name)
        except Resolver404:  # エンドポイント未解決404ケア
            pass
        return (method, path)

    def wrapped_generic(self, method, path, *args, **kwargs):
        ql.reset()
        resp = orig_generic(self, method, path, *args, **kwargs)
        req = getattr(resp, "wsgi_request", None)
        if req and getattr(req, "resolver_match", None):
            url_name = req.resolver_match.url_name or req.path_info
            ep_key = (method.upper(), url_name)
        else:
            ep_key = endpoint_key_from(method.upper(), path)
        aggregator.merge(ep_key, ql)
        return resp

    monkeypatch.setattr(APIClient, "generic", wrapped_generic, raising=True)

    with connection.execute_wrapper(ql):
        yield
