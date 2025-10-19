# Full Stack Recipe Search Platform (FastAPI + React.js) and Opensearch

This is a FastAPI-based API that provides recipe search functionality. The API interacts with an OpenSearch instance to perform various search and filtering operations on a collection of recipes. It supports searching by query keywords, filtering by category, ingredients, and nutritional information, and retrieving available categories and ingredients from the dataset. This project consists of a **FastAPI** backend and a **React.js** frontend for a recipe search platform. This guide will help you clone the repository and set it up on your local machine.

## Features

- **Search Recipes**: Search for recipes using keywords in titles, ingredients, or instructions, with additional filters such as categories, ingredients, ratings, and protein content.
- **Filter by Categories**: Retrieve a list of unique categories from the dataset.
- **Filter by Ratings**: Retrieve a list baed on the ratings from the dataset.
- **Pagination**: Supports pagination for search results.

## Prerequisites

Make sure you have the following installed:

- **Python 3.8+**
- **Node.js** and **npm** (or **yarn**)
- **Git**
- **OpenSearch**

### 1. Clone the Repository

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/Prasanth3699/recipes_search_platform
   cd recipes_search_platform
   ```
2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use 'venv\\Scripts\\activate'
   ```

3. Navigate to the backend folder:

   ```bash
   cd backend
   ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Creat an **.env** file with the necessary environment variables
   ```bash
   OPENSEARCH_HOST=<your_opensearch_host>
   OPENSEARCH_PORT=<your_opensearch_port>
   OPENSEARCH_USERNAME=<your_opensearch_username>
   OPENSEARCH_PASSWORD=<your_opensearch_password>
   ```

## Setup OpenSearch Script

This part contains a Python script designed to index recipe data into an OpenSearch cluster. The dataset used is sourced from [Kaggle's Epicurious Recipes dataset](https://www.kaggle.com/datasets/hugodarwood/epirecipes), which provides a collection of recipes including information like ingredients, categories, calories, and ratings.

## Requirement

- OpenSearch cluster instance

### Dataset

The dataset used in this script can be downloaded from Kaggle using the following link: [Epicurious Recipes dataset](https://www.kaggle.com/datasets/hugodarwood/epirecipes). Once downloaded, place the dataset in a `data/epirecipes` folder and ensure the path in the script matches.

### Running the Script

Once the environment is set up, you can run the script as follows:
Below file contains on Scripts folder

```bash
python index_data.py
```

This will connect to the OpenSearch cluster and index all recipes from the dataset.

## How It Works

- Environment Setup: The script loads the OpenSearch connection details (host, port, username, and password) from a .env file using the python-dotenv library.
  OpenSearch Client Initialization: The client is configured to connect securely to an OpenSearch cluster.
- Index Mapping: A custom mapping is created for the epirecipes index, defining various fields such as title, ingredients, categories, and nutritional information.
- Data Loading: The dataset is loaded from a JSON file, and the data is processed into individual documents.
- Bulk Indexing: The documents are indexed in bulk into the OpenSearch cluster.

## Additional Information

- This script assumes the OpenSearch cluster is already running and accessible via the provided host and port.
- It creates the index if it does not exist already.
- For bulk indexing, the script uses the helpers.bulk method from opensearch-py.

### 2. Backend Setup (FastAPI)

1. Navigate to the backend folder:

   ```bash
   cd backend
   ```

2. Run the FastAPI backend:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend will be running on \`http://localhost:8000\`.

### 3. Frontend Setup (Vite)

1. Navigate to the frontend folder:

   ```bash
   cd ../frontend
   ```

2. Install the frontend dependencies:

   ```bash
   npm install
   ```

3. Create a **.env** file in the frontend folder with the following content:

   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend will be running on \`http://localhost:5173\` (or a different port, depending on availability).

### 4. CORS Configuration for FastAPI

To allow communication between the React frontend and FastAPI backend, add CORS middleware to the FastAPI app:

In **main.py**:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",  # Frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Running Both Frontend and Backend Together

1. **Start the backend**:

   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start the frontend**:
   Open a new terminal window and run:
   ```bash
   cd frontend
   npm run dev
   ```

Now, your Vite-based React frontend will communicate with the FastAPI backend for recipe searching.

## YouTube Link [![YouTube](https://img.shields.io/badge/YouTube-red?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/0-QUEUUmTTY)

[![Recipe Search Platform - YouTube](https://img.youtube.com/vi/0-QUEUUmTTY/0.jpg)](https://youtu.be/0-QUEUUmTTY)

### Thank You
