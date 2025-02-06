# Import resources
from services.category_service import Category

# Add resources to the API
def add_resources(api):
    api.add_resource(Category, "/api/category")