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






```
Certainly! I'll provide a comprehensive documentation for the Game Data Analytics API. This documentation will cover how to use the API, including examples of different query types and the expected responses.

# Game Data Analytics API Documentation

## Base URL

```
http://localhost:8000/api/
```

## Endpoints

### 1. Query Game Data

Endpoint: `/query/`
Method: GET

This endpoint allows you to query the game data based on various parameters. It supports different types of fields and operations.

#### Query Parameters

You can use any field from the GameData model as a query parameter. The behavior of the query depends on the field type:

- Numeric Fields (Integer, Float, Decimal):
  - Supports exact match, greater than, and less than operations.
  - Example: `AppID=100`, `Price>10`, `Required_age<18`

- String Fields (Char, Text):
  - Supports case-insensitive substring matching.
  - Example: `Name=strategy`, `Developers=valve`

- Date Fields:
  - Supports exact date matching.
  - Format: YYYY-MM-DD
  - Example: `Release_date=2022-01-01`

- Boolean Fields:
  - Accepts 'true' or 'false' (case-insensitive).
  - Example: `Windows=true`, `Mac=false`

#### Response Format

The API responds with a JSON object containing two main sections:

1. `results`: An array of game data objects matching the query.
2. `aggregate_results`: (For numeric fields only) An object containing aggregate statistics.

#### Examples

1. Query by name (substring match):
   ```
   GET /api/query/?Name=strategy
   ```

2. Query by price (greater than operation):
   ```
   GET /api/query/?Price>20
   ```

3. Query by release date:
   ```
   GET /api/query/?Release_date=2022-01-01
   ```

4. Query by multiple parameters:
   ```
   GET /api/query/?Developers=valve&Price<50&Windows=true
   ```

#### Sample Response

```json
{
  "results": [
    {
      "AppID": 570,
      "Name": "Dota 2",
      "Release_date": "2013-07-09",
      "Required_age": 0,
      "Price": 0.00,
      "DLC_count": 0,
      "About_the_game": "...",
      "Supported_languages": "...",
      "Windows": true,
      "Mac": true,
      "Linux": true,
      "Positive": 1371793,
      "Negative": 223107,
      "Score_rank": "...",
      "Developers": "Valve",
      "Publishers": "Valve",
      "Categories": "...",
      "Genres": "...",
      "Tags": "..."
    },
    // ... more results
  ],
  "aggregate_results": {
    "Price": {
      "avg": 14.99,
      "max": 59.99,
      "min": 0.00,
      "sum": 149900.00,
      "count": 10000
    }
  }
}
```

### 2. Get Columns

Endpoint: `/columns/`
Method: GET

This endpoint returns a list of all available columns in the GameData model.

#### Response Format

An array of column names.

#### Example

```
GET /api/columns/
```

Sample Response:
```json
[
  "AppID",
  "Name",
  "Release_date",
  "Required_age",
  "Price",
  "DLC_count",
  "About_the_game",
  "Supported_languages",
  "Windows",
  "Mac",
  "Linux",
  "Positive",
  "Negative",
  "Score_rank",
  "Developers",
  "Publishers",
  "Categories",
  "Genres",
  "Tags"
]
```

## Error Handling

The API will return appropriate HTTP status codes for different scenarios:

- 200 OK: Successful request
- 400 Bad Request: Invalid query parameters
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server-side error

Error responses will include a JSON object with an `error` key describing the issue.

## Notes

- All queries are case-insensitive for string fields.
- Numeric comparisons (>, <, =) are only available for numeric fields.
- Aggregate results are only provided for numeric fields.
- The API does not support pagination by default. For large datasets, consider implementing pagination to improve performance.

This documentation provides a comprehensive guide on how to use the Game Data Analytics API. It covers the available endpoints, query parameters, response formats, and includes examples for different types of queries. Users can refer to this documentation to understand how to effectively query and analyze the game data using the API.