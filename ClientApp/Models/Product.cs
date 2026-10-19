using System.Text.Json.Serialization;

namespace ClientApp.Models;

public sealed class Product
{
    // Missing fields must throw JsonException rather than silently becoming zero.
    [JsonRequired]
    public int Id { get; set; }

    [JsonRequired]
    public string Name { get; set; } = string.Empty;

    [JsonRequired]
    public decimal Price { get; set; }

    [JsonRequired]
    public int Stock { get; set; }

    [JsonRequired]
    public Category? Category { get; set; }
}
