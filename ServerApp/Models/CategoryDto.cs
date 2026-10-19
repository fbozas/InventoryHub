namespace ServerApp.Models;

// A category is embedded in each product JSON object.
public sealed record CategoryDto(int Id, string Name);
