"""Validate InventoryHub productlist JSON without external Python packages.

Usage: python scripts/validate_contract.py contracts/productlist.example.json
This mirrors the shape in contracts/productlist.schema.json, including the
nested category and restrictions on unexpected fields.
"""

import json
import math
import sys
from decimal import Decimal
from pathlib import Path


def _no_duplicate_properties(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON property: {key}")
        result[key] = value
    return result


def _no_nonfinite_number(constant):
    raise ValueError(f"Not a valid JSON number: {constant}")


def parse_json_document(raw):
    """Parse strict JSON, rejecting NaN, Infinity and repeated keys."""
    return json.loads(
        raw,
        object_pairs_hook=_no_duplicate_properties,
        parse_float=Decimal,
        parse_constant=_no_nonfinite_number,
    )


def validate_products(products):
    """Raise ValueError on a schema mismatch; return products if valid."""
    if not isinstance(products, list):
        raise ValueError("Root must be an array")

    expected_product_keys = {"id", "name", "price", "stock", "category"}
    expected_category_keys = {"id", "name"}
    for index, product in enumerate(products):
        if not isinstance(product, dict) or set(product) != expected_product_keys:
            raise ValueError(f"Product {index}: incorrect keys or object type")
        if type(product["id"]) is not int or product["id"] <= 0:
            raise ValueError(f"Product {index}: invalid id")
        if not isinstance(product["name"], str) or not product["name"].strip():
            raise ValueError(f"Product {index}: invalid name")
        if type(product["price"]) not in (int, float, Decimal) or (
            not math.isfinite(product["price"]) or product["price"] < 0
        ):
            raise ValueError(f"Product {index}: invalid price")
        if type(product["stock"]) is not int or product["stock"] < 0:
            raise ValueError(f"Product {index}: invalid stock")
        category = product["category"]
        if not isinstance(category, dict) or set(category) != expected_category_keys:
            raise ValueError(f"Product {index}: invalid category structure")
        if type(category["id"]) is not int or category["id"] <= 0:
            raise ValueError(f"Product {index}: invalid category id")
        if not isinstance(category["name"], str) or not category["name"].strip():
            raise ValueError(f"Product {index}: invalid category name")

    return products


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/validate_contract.py FILE.json")
    source = Path(sys.argv[1])
    try:
        validate_products(parse_json_document(source.read_text(encoding="utf-8")))
    except (ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
    print(f"PASS: valid InventoryHub productlist contract ({source})")
