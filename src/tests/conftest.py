import shutil
import pathlib

from django.db import connections
from django.urls import resolve, Resolver404
from rest_framework.test import APIClient
import pytest

from .table_operated_tracker import EndpointCrudAggregator, SQLOperatedTracker

HERE = pathlib.Path(__file__).parent


@pytest.fixture(scope="session", autouse=True)
def write_endpoint_reports_after_session(request):
    outdir = HERE / "docs"
    shutil.rmtree(outdir)
    aggregator = EndpointCrudAggregator(outdir=outdir)
    request.config._endpoint_crud_aggregator = aggregator
    yield
    aggregator.write_files()


@pytest.fixture(autouse=True)
def collect_crud_by_endpoint(request, monkeypatch):
    aggregator: EndpointCrudAggregator = request.config._endpoint_crud_aggregator
    collector = SQLOperatedTracker()

    # DB execute wrapper
    exits = []
    for conn in connections.all():
        cm = conn.execute_wrapper(collector)
        cm.__enter__()
        exits.append(cm)

    orig_generic = APIClient.generic

    def endpoint_key_from(method: str, path: str) -> tuple[str, str]:
        try:
            m = resolve(path)
            return (method, m.url_name)
        except Resolver404:  # エンドポイント未解決404ケア
            pass
        return (method, path)

    def wrapped_generic(self, method, path, *args, **kwargs):
        collector.reset()  # HTTPごとにSQL集計をクリア
        resp = orig_generic(self, method, path, *args, **kwargs)
        req = getattr(resp, "wsgi_request", None)
        if req and getattr(req, "resolver_match", None):
            url_name = req.resolver_match.url_name or req.path_info
            ep_key = (method.upper(), url_name)
        else:
            ep_key = endpoint_key_from(method.upper(), path)
        aggregator.merge(ep_key, collector)
        return resp

    monkeypatch.setattr(APIClient, "generic", wrapped_generic, raising=True)

    yield

    for cm in exits:
        cm.__exit__(None, None, None)
