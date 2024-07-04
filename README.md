# segwise-intern-assignment


# Game Analytics API

This assignment/project is a Django-based REST API for game analytics. It allows users to upload CSV data containing game information and query this data using various filters and aggregations.

## Table of Contents

1. [Installation](#installation)
2. [Project Structure](#project-structure)
3. [API Endpoints](#api-endpoints)
4. [Authentication](#authentication)
5. [Docker Deployment](#docker-deployment)
6. [Usage Examples](#usage-examples)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/RajendraKumarVesapogu/segwise-intern-assignment.git
   cd segwise-intern-assignment
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   # On linux, use, `source .venv/bin/activate`
   # On Windows, use `.venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   python manage.py migrate
   ```

5. Create a superuser (for admin access):
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

The API should now be accessible at `http://localhost:8000/`.

## Project Structure
```
game_analytics_api/  # Main Django app
├── game_analytics/
    ├── migrations/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py       # Contains GameData model
    ├── serializers.py  # Contains GameDataSerializer
    ├── views.py         # Contains API views
    └── urls.py         # URL configurations for the app

game_analytics_project/  # Project configuration
├── __init__.py
├── asgi.py
├── settings.py
├── urls.py
└── wsgi.py

templates/  # HTML templates (if any)

static/     # Static files (CSS, JS, etc.)

manage.py
requirements.txt
Dockerfile
docker-compose.yml
README.md
```
## API Endpoints

### 1. CSV Upload
- **URL:** `/api/upload/`
- **Method:** POST
- **Auth Required:** Yes
- **Data Params:** 
  ```json
  {
    "csv_url": "[url to CSV file]"
  }
  ```
- **Success Response:** 
  - Code: 201
  - Content: `{"message": "CSV data uploaded successfully"}`

### 2. Data Query
- **URL:** `/api/query/`
- **Method:** GET
- **Auth Required:** Yes
- **URL Params:** 
  - Any field from the GameData model (e.g., `Name`, `Price`, `Release_date`)
  - `aggregations`: Comma-separated list of aggregate functions (avg, max, min, sum)
  - `agg_field`: Field to apply aggregations to
- **Success Response:** 
  - Code: 200
  - Content: List of matching GameData objects or aggregation results

## Authentication

This API uses JWT (JSON Web Token) authentication. To authenticate:

1. Obtain a token:
   - **URL:** `/api/token/`
   - **Method:** POST
   - **Data Params:** 
     ```json
     {
       "username": "[valid username]",
       "password": "[valid password]"
     }
     ```
   - **Success Response:**
     - Code: 200
     - Content: `{"access":"[access_token]","refresh":"[refresh_token]"}`

2. Use the access token in the Authorization header for subsequent requests:
   ```
   Authorization: Bearer [access_token]
   ```

## Docker Deployment

1. Build the Docker image:
   ```
   docker-compose build
   ```

2. Run the Docker container:
   ```
   docker-compose up
   ```

The API will be available at `http://localhost:8000/`.

## Usage Examples

1. Upload CSV data:
   ```
   curl -X POST -H "Authorization: Bearer [your_token]" -H "Content-Type: application/json" -d '{"csv_url":"https://example.com/game_data.csv"}' http://localhost:8000/api/upload/
   ```

2. Query data:
   ```
   curl -H "Authorization: Bearer [your_token]" "http://localhost:8000/api/query/?Name=Half-Life&Price=9.99"
   ```

3. Aggregate query:
   ```
   curl -H "Authorization: Bearer [your_token]" "http://localhost:8000/api/query/?aggregations=avg,max&agg_field=Price"
   ```

## Additional Notes

- Ensure that your CSV file structure matches the fields in the GameData model.
- For large datasets, consider implementing pagination in the query endpoint.
- The project uses SQLite by default. For production, consider switching to a more robust database like PostgreSQL.
- Always keep your secret key and sensitive information secure and out of version control.

For any issues or feature requests, please open an issue in the GitHub repository.
```

This README provides a comprehensive guide to your project, including setup instructions, project structure, API documentation, and usage examples. You may want to adjust some details based on your specific implementation or add more sections as needed.