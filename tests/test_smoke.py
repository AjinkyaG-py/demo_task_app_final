from app import create_app


def test_create_app_and_blueprints():
    app = create_app()
    assert app is not None
    # Check that major blueprints are registered
    assert 'login_page' in app.blueprints
    assert 'techpub_leads' in app.blueprints
    assert 'writers' in app.blueprints
    assert 'development_leads' in app.blueprints


def test_home_route_returns_200():
    app = create_app()
    app.config["WTF_I18N_ENABLED"] = False
    with app.test_client() as client:
        resp = client.get('/')
        assert resp.status_code in (200, 302)


def test_protected_routes_require_login():
    app = create_app()
    app.config["WTF_I18N_ENABLED"] = False
    protected_urls = [
        '/techpub_leads/landing',
        '/writers/landing',
        '/development_leads/landing',
        '/writers/timesheet',
    ]
    with app.test_client() as client:
        for url in protected_urls:
            resp = client.get(url, follow_redirects=False)
            # Unauthenticated requests should redirect (302) to login
            assert resp.status_code in (302, 401)
