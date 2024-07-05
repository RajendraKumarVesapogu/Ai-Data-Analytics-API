Sure! Here is the brief documentation for your API endpoint in Markdown format:

# GameData Query API

## Endpoint

### `GET /api/query/`

This endpoint allows querying the `GameData` model with dynamic filters and supports aggregate functions.

## Query Parameters

- **field**: The target column to perform the query on.
- **operator**: The logical operator to use (`=`, `<`, `>`, `<=`, `>=`).
- **value**: The value to search for.
- **agg_function_field**: Aggregate function to apply on a specific field.

## Usage

### Examples

#### Basic Query
- Query for games with `Required_age` less than or equal to 12:
  ```
  GET /api/query/?field=Required_age__<=__12
  ```

- Query for games released after July 5, 2023:
  ```
  GET /api/query/?field=Release_date__>=__2023-07-05
  ```

#### String Matching
- Query for games with names containing "Raj":
  ```
  GET /api/query/?field=Name__icontains__Raj
  ```

#### Aggregate Functions
- Get the sum of positive reviews:
  ```
  GET /api/query/?agg_sum_Positive=total
  ```

- Get the maximum required age:
  ```
  GET /api/query/?agg_max_Required_age=max_age
  ```

- Get the average price:
  ```
  GET /api/query/?agg_mean_Price=average_price
  ```

## Response

### Success Response
- **Code**: 200 OK
- **Content**: A list of `GameData` objects or an aggregate result

Example Response for a basic query:
```json
[
  {
    "AppID": 123,
    "Name": "Sample Game",
    "Release_date": "2023-01-01",
    "Required_age": 12,
    "Price": "19.99",
    "DLC_count": 3,
    "About_the_game": "Sample description.",
    "Supported_languages": "English, Spanish",
    "Windows": true,
    "Mac": false,
    "Linux": true,
    "Positive": 1500,
    "Negative": 300,
    "Score_rank": "Top 10%",
    "Developers": "Sample Developer",
    "Publishers": "Sample Publisher",
    "Categories": "Action, Adventure",
    "Genres": "Action, Indie",
    "Tags": "Singleplayer, Indie"
  }
]
```

Example Response for an aggregate query:
```json
{
  "result": 5000
}
```

## Error Responses
- **Code**: 400 BAD REQUEST
- **Content**: Error message explaining the invalid query

Example:
```json
{
  "error": "Invalid query parameter: field=UnknownField"
}
```

## Notes
- **Exact Match for Numerical Fields**: Use `=` for exact matches, e.g., `field=Required_age__=__20`.
- **Substring Match for String Fields**: Use `icontains` operator, e.g., `field=Name__icontains__Raj`.
- **Date Fields**: Support exact matches and range queries with `<`, `>`, `<=`, `>=`.
- **Aggregate Functions**: Supported functions are `sum`, `max`, `min`, and `mean`.

This endpoint allows for flexible and powerful querying of the `GameData` model, making it easy to filter and aggregate data based on various criteria.
```