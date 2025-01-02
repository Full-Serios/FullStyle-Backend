import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from config.server_config import create_app, db
from models.service_model import ServiceModel
from models.site_model import SiteModel
from models.worker_model import WorkerModel
from models.worker_has_service_model import WorkerHasServiceModel
from models.site_has_service_model import SiteHasServiceModel
from models.category_model import CategoryModel
from models.site_has_category_model import SiteHasCategoryModel

@pytest.fixture(scope='module')
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()

@pytest.fixture(autouse=True)
def run_around_tests():
    # Code to run before each test
    yield
    # Code to run after each test
    db.session.rollback()

def test_create_service(client):
    response = client.post("/api/service", json={
        "id": 0,
        "name": "Corte sencillo",
        "description": "A simple haircut",
        "price": 10.0,
        "duration": 30,
        "category_id": 1
    })
    assert response.status_code == 201
    assert response.json['name'] == "Corte sencillo"

def test_get_service_by_id(client):
    response = client.get("/api/service/query", query_string={"id": 1})
    print(response.json)
    assert response.status_code == 200
    assert response.json['id'] == 1

def test_get_service_by_name(client):
    response = client.get("/api/service/query", query_string={"name": "Corte sencillo"})
    assert response.status_code == 200
    assert response.json['name'] == "Corte sencillo"

def test_get_service_by_category(client):
    response = client.get("/api/service/query", query_string={"category_id": 1})
    assert response.status_code == 200
    assert response.json[0]['category_id'] == 1

def test_get_all_categories(client):
    response = client.get("/api/category")
    assert response.status_code == 200
    assert len(response.json) > 0

def test_create_site(client):
    response = client.post("/api/site", json={
        "id": 0,
        "name": "Main Site",
        "address": "123 Main St",
        "phone": "123-456-7890",
        "manager_id": 1
    })
    assert response.status_code == 201
    assert response.json['name'] == "Main Site"

def test_get_all_sites(client):
    response = client.get("/api/site")
    assert response.status_code == 200
    assert len(response.json) > 0

def test_create_worker(client):
    response = client.post("/api/worker", json={
        "id": 0,
        "name": "John Doe",
        "availability": {},
        "busy": False,
        "site_id": 0,
        "site_manager_id": 1
    })
    assert response.status_code == 201
    assert response.json['name'] == "John Doe"

def test_get_all_workers(client):
    response = client.get("/api/worker")
    assert response.status_code == 200
    assert len(response.json) > 0

def test_create_site_has_service(client):
    response = client.post("/api/site_has_service", json={
        "site_id": 0,
        "site_manager_id": 1,
        "service_id": 0
    })
    assert response.status_code == 201
    assert response.json['site_id'] == 0

def test_get_all_site_has_services(client):
    response = client.get("/api/site_has_service")
    assert response.status_code == 200
    assert len(response.json) > 0

def test_create_worker_has_service(client):
    response = client.post("/api/worker_has_service", json={
        "worker_id": 0,
        "service_id": 0
    })
    assert response.status_code == 201
    assert response.json['worker_id'] == 0

def test_get_all_worker_has_services(client):
    response = client.get("/api/worker_has_service")
    assert response.status_code == 200
    assert len(response.json) > 0

def test_create_site_has_category(client):
    response = client.post("/api/site_has_category", json={
        "site_id": 0,
        "category_id": 1
    })
    assert response.status_code == 201
    assert response.json['site_id'] == 0

def test_get_all_site_has_categories(client):
    response = client.get("/api/site_has_category")
    assert response.status_code == 200
    assert len(response.json) > 0

@pytest.fixture(scope='module', autouse=True)
def clean_up():
    yield
    with create_app().app_context():
        # Clean up all test data
        worker_service = WorkerHasServiceModel.query.filter_by(worker_id=0, service_id=0).first()
        if worker_service:
            db.session.delete(worker_service)
        
        site_service = SiteHasServiceModel.query.filter_by(site_id=0, site_manager_id=1, service_id=0).first()
        if site_service:
            db.session.delete(site_service)
        
        site_category = SiteHasCategoryModel.query.filter_by(site_id=0, category_id=1).first()
        if site_category:
            db.session.delete(site_category)
        
        worker = WorkerModel.query.filter_by(id=0).first()
        if worker:
            db.session.delete(worker)
        
        site = SiteModel.query.filter_by(id=0).first()
        if site:
            db.session.delete(site)
        
        service = ServiceModel.query.filter_by(id=0).first()
        if service:
            db.session.delete(service)
        
        db.session.commit()