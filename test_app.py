import app

def test_home_page():
    client = app.app.test_client()
    response = client.get('/')
    assert response.status_code == 200

def test_login():
    client = app.app.test_client()
    response = client.post('/', data={
        "username": "admin",
        "password": "admin"
    })
    assert response.status_code == 302  # redirect to dashboard

def test_dashboard():
    client = app.app.test_client()
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_books_page():
    client = app.app.test_client()
    response = client.get('/books')
    assert response.status_code == 200

def test_members_page():
    client = app.app.test_client()
    response = client.get('/members')
    assert response.status_code == 200

def test_issue_page():
    client = app.app.test_client()
    response = client.get('/issue')
    assert response.status_code == 200

def test_return_page():
    client = app.app.test_client()
    response = client.get('/return')
    assert response.status_code == 200

def test_reports_page():
    client = app.app.test_client()
    response = client.get('/reports')
    assert response.status_code == 200
def test_invalid_login():
    client = app.app.test_client()
    response = client.post('/', data={
        "username": "wrong",
        "password": "wrong"
    })
    assert response.status_code == 200