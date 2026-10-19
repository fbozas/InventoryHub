namespace ServerApp.Models;

// decimal preserves monetary precision. The JSON response uses camelCase keys.
public sealed record ProductDto(
    int Id,
    string Name,
    decimal Price,
    int Stock,
    CategoryDto Category);
