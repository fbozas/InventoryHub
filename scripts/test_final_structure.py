"""Offline source/config consistency checks; not a substitute for dotnet build."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FinalSourceChecks(unittest.TestCase):
    def test_required_artifacts_exist(self):
        for name in (
            "FullStackSolution.sln", "REFLECTION.md", "PERFORMANCE.md",
            "README.md", "ClientApp/Services/ProductService.cs",
            "ServerApp/Program.cs", "contracts/productlist.schema.json",
            "postman/InventoryHub.Final.postman_collection.json",
        ):
            self.assertTrue((ROOT / name).is_file(), name)

    def test_client_points_to_server_and_correct_route(self):
        api_config = json.loads((ROOT / "ClientApp/wwwroot/appsettings.json").read_text())
        self.assertEqual(api_config["ApiBaseUrl"], "http://localhost:5199/")
        service = (ROOT / "ClientApp/Services/ProductService.cs").read_text()
        self.assertIn('"api/productlist"', service)
        self.assertIn('TimeSpan.FromSeconds(15)', service)
        self.assertIn('_inFlight ??= FetchAndCacheAsync()', service)
        self.assertNotIn('"api/products"', service)

    def test_server_cors_before_output_cache_and_route(self):
        code = (ROOT / "ServerApp/Program.cs").read_text()
        self.assertLess(code.index('app.UseRouting();'), code.index('app.UseCors('))
        self.assertLess(code.index('app.UseCors('), code.index('app.UseOutputCache();'))
        self.assertIn('CacheOutput(productCachePolicy)', code)
        self.assertIn('"/api/productlist"', code)
        self.assertIn('WithOrigins(allowedOrigin)', code)


if __name__ == "__main__":
    unittest.main()
