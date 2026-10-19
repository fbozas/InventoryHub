"""Offline contract unit tests: python -m unittest discover -s scripts -p 'test_*.py'"""
import copy
import json
import unittest
from pathlib import Path

from validate_contract import parse_json_document, validate_products

ROOT = Path(__file__).resolve().parents[1]


class ProductListContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid = parse_json_document(
            (ROOT / "contracts" / "productlist.example.json").read_text(encoding="utf-8")
        )

    def test_example_is_valid(self):
        self.assertEqual(len(validate_products(self.valid)), 2)

    def test_schema_document_is_well_formed(self):
        schema = json.loads((ROOT / "contracts" / "productlist.schema.json").read_text())
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("category", schema["items"]["required"])
        self.assertEqual(schema["items"]["properties"]["category"]["required"], ["id", "name"])

    def test_bad_syntax_is_rejected(self):
        with self.assertRaises(json.JSONDecodeError):
            parse_json_document("{bad json")

    def test_duplicate_property_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_json_document('{"id":1,"id":2}')

    def test_missing_category_is_rejected(self):
        products = copy.deepcopy(self.valid)
        del products[0]["category"]
        with self.assertRaises(ValueError):
            validate_products(products)

    def test_category_null_is_rejected(self):
        products = copy.deepcopy(self.valid)
        products[0]["category"] = None
        with self.assertRaises(ValueError):
            validate_products(products)

    def test_category_missing_name_is_rejected(self):
        products = copy.deepcopy(self.valid)
        del products[0]["category"]["name"]
        with self.assertRaises(ValueError):
            validate_products(products)

    def test_invalid_nested_id_is_rejected(self):
        products = copy.deepcopy(self.valid)
        products[0]["category"]["id"] = 0
        with self.assertRaises(ValueError):
            validate_products(products)

    def test_wrong_root_shape_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_products({"products": self.valid})

    def test_price_as_string_is_rejected(self):
        products = copy.deepcopy(self.valid)
        products[0]["price"] = "1200.50"
        with self.assertRaises(ValueError):
            validate_products(products)

    def test_extra_category_property_is_rejected(self):
        products = copy.deepcopy(self.valid)
        products[0]["category"]["description"] = "Extra"
        with self.assertRaises(ValueError):
            validate_products(products)

    def test_empty_category_name_is_rejected(self):
        products = copy.deepcopy(self.valid)
        products[0]["category"]["name"] = "  "
        with self.assertRaises(ValueError):
            validate_products(products)


if __name__ == "__main__":
    unittest.main()
