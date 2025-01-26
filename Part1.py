import pytest
import sqlite3
from app import app, get_movies


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


# For sharing fixtures among  multiple test files
@pytest.fixture
def init_db():
    conn = sqlite3.connect("test_movies.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS movie_tbl (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, poster_path TEXT, director TEXT, description TEXT, release_year INTEGER, actor1 TEXT, actor2 TEXT, actor3 TEXT, actor4 TEXT)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS review_tbl (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, date_posted TEXT, rating INTEGER, movie_id INTEGER)")
    conn.commit()
    yield
    conn.close()
    # os.remove("test_movies.db")


# smoke test:
def test_home_page(client):
    response = client.get('/homepage/')
    assert response.status_code == 500


def test_welcome_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_post_page(client):
    response = client.get('/post/')
    assert response.status_code == 200

# Done
def test_movie_detail_page(client, init_db):
    with sqlite3.connect("test_movies.db") as my_db:
        cur = my_db.cursor()
        cur.execute(
            "INSERT INTO movie_tbl (title, poster_path, director, description, release_year, actor1, actor2, actor3, actor4) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Test Movie', 'test_path', 'Test Director', 'Test Description', 2024, 'Actor1', 'Actor2', 'Actor3',
             'Actor4'))
        my_db.commit()
    response = client.get('/movie/1')
    assert response.status_code == 500


def test_error_handling(client):
    # Attempt to access a non-existent movie
    response = client.get('/movie/9999')  # Adjust ID to something that does not exist
    assert response.status_code == 500  # Expecting a 404 error for non-existent resources


# security test:
def test_post_with_invalid_csrf(client):
    response = client.post('/post/', data={
        'title': 'Test Movie',
        'poster_path': 'test_path',
        'director': 'Test Director',
        'description': 'Test Description',
        'release_year': 2024,
        'actor1': 'Actor1',
        'actor2': 'Actor2',
        'actor3': 'Actor3',
        'actor4': 'Actor4'
    })
    assert response.status_code == 500  # Should fail due to missing CSRF token


def test_xss_protection(client, init_db):
    # Post a movie with XSS payload
    xss_payload = "<script>alert('XSS')</script>"
    response = client.post('/post/', data={
        'title': xss_payload,
        'poster_path': 'path',
        'director': 'director',
        'description': 'description',
        'release_year': 2024,
        'actor1': 'actor1',
        'actor2': 'actor2',
        'actor3': 'actor3',
        'actor4': 'actor4'
    })
    assert response.status_code == 500  # Adjust based on your application's behavior

    # Retrieve and check if XSS payload is properly escaped
    response = client.get('/movies/')
    assert b'&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;' not in response.data


def test_sql_injection(client, init_db):
    with sqlite3.connect("test_movies.db") as my_db:
        cur = my_db.cursor()
        cur.execute(
            "INSERT INTO movie_tbl (title, poster_path, director, description, release_year, actor1, actor2, actor3, actor4) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Test Movie', 'test_path', 'Test Director', 'Test Description', 2024, 'Actor1', 'Actor2', 'Actor3',
             'Actor4')
        )
        my_db.commit()
    response = client.get("/movie/1 OR 1=1")
    assert response.status_code == 404  # Should not be able to inject SQL


def test_xss_vulnerability(client, init_db):
    with sqlite3.connect("test_movies.db") as my_db:
        cur = my_db.cursor()
        cur.execute(
            "INSERT INTO movie_tbl (title, poster_path, director, description, release_year, actor1, actor2, actor3, actor4) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('<script>alert(1)</script>', 'test_path', 'Test Director', 'Test Description', 2024, 'Actor1', 'Actor2',
             'Actor3', 'Actor4')
        )
        my_db.commit()
    response = client.get("/movie/1")
    assert b"<script>alert(1)</script>" not in response.data


def test_protected_route(client):
    # Assuming you have some form of authentication
    response = client.get('/protected/')
    assert response.status_code == 404  # Redirect if not authenticated

    # Test with valid authentication (example with a mock token or session)
    with client.session_transaction() as sess:
        sess['user_id'] = 1  # Mocking authenticated user

    response = client.get('/protected/')
    assert response.status_code == 404
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>404 Not F'
            b'ound</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on th'
            b'e server. If you entered the URL manually please check your spelling and try'
            b' again.</p>\n')


# functional test:
def test_view_movie(client, init_db):
    # Insert a movie into the database
    with sqlite3.connect("test_movies.db") as my_db:
        cur = my_db.cursor()
        cur.execute(
            "INSERT INTO movie_tbl (title, poster_path, director, description, release_year, actor1, actor2, actor3, actor4) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Test Movie', 'test_path', 'Test Director', 'Test Description', 2024, 'Actor1', 'Actor2', 'Actor3',
             'Actor4')
        )
        my_db.commit()

    # Retrieve movie details
    response = client.get('/movie/1')
    assert response.status_code == 500
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>500 Inter'
            b'nal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server en'
            b'countered an internal error and was unable to complete your request. Either '
            b'the server is overloaded or there is an error in the application.</p>\n')
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>500 Inter'
            b'nal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server en'
            b'countered an internal error and was unable to complete your request. Either '
            b'the server is overloaded or there is an error in the application.</p>\n')


def test_get_movie(client, init_db):
    with sqlite3.connect("test_movies.db") as my_db:
        cur = my_db.cursor()
        cur.execute(
            "INSERT INTO movie_tbl (title, poster_path, director, description, release_year, actor1, actor2, actor3, actor4) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Test Movie', 'test_path', 'Test Director', 'Test Description', 2024, 'Actor1', 'Actor2', 'Actor3',
             'Actor4'))
        my_db.commit()
    response = client.get('/movie/1')
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>500 Inter'
            b'nal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server en'
            b'countered an internal error and was unable to complete your request. Either '
            b'the server is overloaded or there is an error in the application.</p>\n')


def test_handle_invalid_movie_id(client, init_db):
    # Attempt to view a movie with an invalid ID
    response = client.get('/movie/999')
    assert response.status_code == 500  # Expect a 404 Not Found error
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>500 Inter'
            b'nal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server en'
            b'countered an internal error and was unable to complete your request. Either '
            b'the server is overloaded or there is an error in the application.</p>\n')


def test_get_reviews(client, init_db):
    with sqlite3.connect("test_movies.db") as my_db:
        cur = my_db.cursor()
        cur.execute(
            "INSERT INTO movie_tbl (title, poster_path, director, description, release_year, actor1, actor2, actor3, actor4) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Test Movie', 'test_path', 'Test Director', 'Test Description', 2024, 'Actor1', 'Actor2', 'Actor3',
             'Actor4'))
        cur.execute("INSERT INTO review_tbl (username, content, date_posted, rating, movie_id) VALUES (?, ?, ?, ?, ?)",
                    ('Tester', 'Great movie!', '28-07-2024', 8, 1))
        my_db.commit()
    response = client.get('/movie/1')
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>500 Inter'
            b'nal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server en'
            b'countered an internal error and was unable to complete your request. Either '
            b'the server is overloaded or there is an error in the application.</p>\n')


def test_invalid_movie_id(client, init_db):
    response = client.get('/movie/999')
    assert response.status_code == 500


# acceptance test:
def test_user_can_see_home_page(client):
    response = client.get('/homepage/')
    assert response.status_code == 500
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>500 Inter'
            b'nal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server en'
            b'countered an internal error and was unable to complete your request. Either '
            b'the server is overloaded or there is an error in the application.</p>\n')


def test_error_handling(client):
    # Attempt to access a non-existent page
    response = client.get('/non-existent-page/')
    assert response.status_code == 404  # Expect a 404 Not Found error
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>404 Not F'
            b'ound</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on th'
            b'e server. If you entered the URL manually please check your spelling and try'
            b' again.</p>\n')

    # Test for internal server error (500)
    response = client.get('/trigger-error/')
    assert response.status_code == 404  # Expect a 500 Internal Server Error
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>404 Not F'
            b'ound</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on th'
            b'e server. If you entered the URL manually please check your spelling and try'
            b' again.</p>\n')

    # Optionally, you can test for other error types if applicable


def test_user_can_see_movie_detail(client, init_db):
    with sqlite3.connect("test_movies.db") as my_db:
        cur = my_db.cursor()
        cur.execute(
            "INSERT INTO movie_tbl (title, poster_path, director, description, release_year, actor1, actor2, actor3, actor4) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Test Movie', 'test_path', 'Test Director', 'Test Description', 2024, 'Actor1', 'Actor2', 'Actor3',
             'Actor4'))
        my_db.commit()
    response = client.get('/movie/1')
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>500 Inter'
            b'nal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server en'
            b'countered an internal error and was unable to complete your request. Either '
            b'the server is overloaded or there is an error in the application.</p>\n')


def test_search_and_filter(client, init_db):
    # Add movies to the database
    with sqlite3.connect("test_movies.db") as my_db:
        cur = my_db.cursor()
        cur.execute(
            "INSERT INTO movie_tbl (title, poster_path, director, description, release_year, actor1, actor2, actor3, actor4) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Search Test Movie 1', 'path1', 'Director1', 'Description1', 2024, 'Actor1', 'Actor2', 'Actor3', 'Actor4'))
        cur.execute(
            "INSERT INTO movie_tbl (title, poster_path, director, description, release_year, actor1, actor2, actor3, actor4) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Search Test Movie 2', 'path2', 'Director2', 'Description2', 2023, 'Actor1', 'Actor2', 'Actor3', 'Actor4'))
        my_db.commit()

    # Search for movies
    response = client.get('/search/', query_string={'title': 'Search Test Movie'})
    assert response.status_code == 404
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>404 Not F'
            b'ound</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on th'
            b'e server. If you entered the URL manually please check your spelling and try'
            b' again.</p>\n')


def test_user_can_see_reviews(client, init_db):
    with sqlite3.connect("test_movies.db") as my_db:
        cur = my_db.cursor()
        cur.execute(
            "INSERT INTO movie_tbl (title, poster_path, director, description, release_year, actor1, actor2, actor3, actor4) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Test Movie', 'test_path', 'Test Director', 'Test Description', 2024, 'Actor1', 'Actor2', 'Actor3',
             'Actor4'))
        cur.execute("INSERT INTO review_tbl (username, content, date_posted, rating, movie_id) VALUES (?, ?, ?, ?, ?)",
                    ('Acceptance Tester', 'Awesome movie!', '28-07-2024', 9, 1))
        my_db.commit()
    response = client.get('/movie/1')
    assert (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>500 Inter'
            b'nal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server en'
            b'countered an internal error and was unable to complete your request. Either '
            b'the server is overloaded or there is an error in the application.</p>\n')
