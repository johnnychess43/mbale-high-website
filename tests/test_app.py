import pytest

import app as website


@pytest.fixture()
def client(monkeypatch, tmp_path):
    website.app.config.update(TESTING=True, SECRET_KEY="test-session-secret", DATABASE_PATH=str(tmp_path / "test_admin.db"), UPLOAD_FOLDER=str(tmp_path / "uploads"))
    website.init_admin_storage()
    monkeypatch.setattr(website, "ADMIN_USERNAME", "test-admin")
    monkeypatch.setattr(website, "ADMIN_PASSWORD", "test-password")
    with website.app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize(
    "path",
    ["/", "/about", "/academics", "/news", "/gallery", "/contact", "/fees"],
)
def test_main_pages_render(client, path):
    response = client.get(path)
    assert response.status_code == 200, path
    assert response.content_type.startswith("text/html")


def test_all_pathways_and_subject_pages_render(client):
    for pathway_key, pathway in website.PATHWAYS.items():
        response = client.get(f"/pathways/{pathway_key}")
        assert response.status_code == 200, f"pathway: {pathway_key}"

        for subject_key in pathway["subjects"]:
            response = client.get(f"/pathways/{pathway_key}/{subject_key}")
            assert response.status_code == 200, (
                f"subject: {pathway_key}/{subject_key}"
            )

            for resource_key in website.RESOURCE_TYPES:
                response = client.get(
                    f"/pathways/{pathway_key}/{subject_key}/{resource_key}"
                )
                assert response.status_code == 200, (
                    f"resource: {pathway_key}/{subject_key}/{resource_key}"
                )


def test_unknown_pathway_subject_and_resource_return_404(client):
    assert client.get("/pathways/not-a-pathway").status_code == 404
    assert client.get("/pathways/stem/not-a-subject").status_code == 404
    assert client.get("/pathways/stem/mathematics/not-a-resource").status_code == 404
    assert client.get("/this-page-does-not-exist").status_code == 404


def test_admin_requires_login(client):
    response = client.get("/admin")
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_login_sets_session_and_logout_clears_it(client):
    response = client.post(
        "/admin/login",
        data={"username": "test-admin", "password": "test-password"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")

    dashboard = client.get("/admin")
    assert dashboard.status_code == 200
    assert b"Admin Dashboard" in dashboard.data

    logout = client.get("/admin/logout", follow_redirects=False)
    assert logout.status_code == 302
    assert client.get("/admin").status_code == 302


def test_admin_rejects_invalid_credentials(client):
    response = client.post(
        "/admin/login",
        data={"username": "wrong", "password": "wrong"},
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_admin_sections_require_login(client):
    for section_key in website.ADMIN_SECTIONS:
        response = client.get(f"/admin/sections/{section_key}")
        assert response.status_code == 302
        assert "/admin/login" in response.headers["Location"]


def test_all_admin_sections_render_after_login(client):
    client.post(
        "/admin/login",
        data={"username": "test-admin", "password": "test-password"},
    )
    for section_key, section in website.ADMIN_SECTIONS.items():
        response = client.get(f"/admin/sections/{section_key}")
        assert response.status_code == 200, section_key
        assert section["title"].encode() in response.data
        assert b"Back to Dashboard" in response.data


def test_unknown_admin_section_returns_404_after_login(client):
    client.post(
        "/admin/login",
        data={"username": "test-admin", "password": "test-password"},
    )
    assert client.get("/admin/sections/not-a-section").status_code == 404


def test_dashboard_has_links_for_all_admin_sections(client):
    client.post(
        "/admin/login",
        data={"username": "test-admin", "password": "test-password"},
    )
    response = client.get("/admin")
    assert response.status_code == 200
    for section_key in website.ADMIN_SECTIONS:
        assert f"/admin/sections/{section_key}".encode() in response.data



def test_admin_can_create_edit_and_delete_news_item(client):
    client.post("/admin/login", data={"username": "test-admin", "password": "test-password"})
    created = client.post("/admin/sections/news", data={
        "action": "create", "title": "Sports Day", "description": "Annual sports day update"
    }, follow_redirects=True)
    assert created.status_code == 200
    assert b"Sports Day" in created.data
    assert b"Item added" in created.data

    with website.db_connect() as connection:
        item_id = connection.execute("SELECT id FROM content_items WHERE section = 'news'").fetchone()["id"]

    edited = client.post(f"/admin/sections/news?edit={item_id}", data={
        "action": "update", "item_id": str(item_id), "title": "Updated Sports Day",
        "description": "New event details"
    }, follow_redirects=True)
    assert edited.status_code == 200
    assert b"Updated Sports Day" in edited.data

    public_page = client.get("/news")
    assert b"Updated Sports Day" in public_page.data

    deleted = client.post("/admin/sections/news", data={
        "action": "delete", "item_id": str(item_id)
    }, follow_redirects=True)
    assert deleted.status_code == 200
    assert b"Updated Sports Day" not in deleted.data


def test_admin_can_upload_learning_material(client):
    from io import BytesIO

    client.post("/admin/login", data={"username": "test-admin", "password": "test-password"})
    response = client.post("/admin/sections/resources", data={
        "title": "Form 4 Revision", "description": "Mathematics revision paper",
        "file": (BytesIO(b"%PDF-test-content"), "revision.pdf")
    }, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert b"Form 4 Revision" in response.data
    assert b"Open / download file" in client.get("/academics").data


def test_editor_cannot_manage_sensitive_admin_sections(client):
    client.post("/admin/login", data={"username": "test-admin", "password": "test-password"})
    client.post("/admin/sections/users", data={
        "username": "limited-editor", "password": "long-secure-password",
        "role": "editor"
    })
    client.get("/admin/logout")
    login = client.post("/admin/login", data={
        "username": "limited-editor", "password": "long-secure-password"
    })
    assert login.status_code == 302
    assert client.get("/admin/sections/users").status_code == 403
    assert client.get("/admin/sections/payments").status_code == 403
