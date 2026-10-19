"""Smoke tests against the running Minimal API (no extra packages).

Start ServerApp in Development, then run from solution root:
python scripts/smoke_test.py
"""
from decimal import Decimal
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from validate_contract import parse_json_document, validate_products

base_url = "http://localhost:5199"
origin = "http://localhost:5150"
endpoint = f"{base_url}/api/productlist"

# 1. Live endpoint returns valid camelCase JSON, including a nested category.
request = Request(endpoint, headers={"Origin": origin})
with urlopen(request, timeout=5) as response:
    assert response.status == 200, f"Unexpected HTTP status: {response.status}"
    assert "application/json" in response.headers.get("Content-Type", ""), "Expected JSON"
    assert response.headers.get("Access-Control-Allow-Origin") == "*", "Development CORS missing"
    raw = response.read().decode("utf-8")
products = validate_products(parse_json_document(raw))
assert len(products) == 2, "Expected exactly two products"
assert [
    (p["id"], p["name"], p["price"], p["stock"], p["category"]["id"], p["category"]["name"])
    for p in products
] == [
    (1, "Laptop", Decimal("1200.50"), 25, 101, "Electronics"),
    (2, "Headphones", Decimal("50.00"), 100, 102, "Accessories"),
], "Unexpected product contents"
print("PASS: GET /api/productlist returns valid products and nested categories")

# 1b. Output cache saves repeat endpoint executions for the next 30 seconds.
# If these GETs fall on the cache-expiration boundary, retry the test.
from urllib.request import urlopen as _urlopen
with _urlopen(Request(endpoint, headers={"Origin": origin}), timeout=5) as first:
    generation_a = first.headers.get("X-InventoryHub-Generation")
    assert generation_a is not None, "Generation diagnostic header missing"
with _urlopen(Request(endpoint, headers={"Origin": origin}), timeout=5) as second:
    generation_b = second.headers.get("X-InventoryHub-Generation")
assert generation_a == generation_b, (
    f"Output caching did not reuse the endpoint response: {generation_a} vs {generation_b}"
)
print(f"PASS: successive GETs reuse server cache generation {generation_a}")

# 2. Development CORS preflight allows requests from the Blazor origin.
preflight = Request(
    endpoint,
    method="OPTIONS",
    headers={
        "Origin": origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "content-type",
    },
)
with urlopen(preflight, timeout=5) as response:
    assert response.status in (200, 204), "CORS preflight failed"
    assert response.headers.get("Access-Control-Allow-Origin") == "*", "CORS origin blocked"
    assert "GET" in response.headers.get("Access-Control-Allow-Methods", "").upper(), "GET blocked"
print("PASS: Development CORS preflight allows GET")

# 3. Obsolete Activity 1 route is not exposed.
try:
    urlopen(f"{base_url}/api/products", timeout=5)
except HTTPError as error:
    assert error.code == 404, f"Expected 404, got {error.code}"
else:
    raise AssertionError("Legacy /api/products unexpectedly exists")
print("PASS: legacy route returns HTTP 404")
