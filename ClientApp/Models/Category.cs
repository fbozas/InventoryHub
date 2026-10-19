using System.Text.Json.Serialization;

namespace ClientApp.Models;

public sealed class Category
{
    [JsonRequired]
    public int Id { get; set; }

    [JsonRequired]
    public string Name { get; set; } = string.Empty;
}
