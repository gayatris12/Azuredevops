"""Test cases for nested blueprint URL prefix dynamic calculation."""
import pytest
import flask


def test_blueprint_url_prefix_original():
    """Test that url_prefix returns the original value set during initialization."""
    bp = flask.Blueprint("test", __name__, url_prefix="/test")

    assert bp.url_prefix == "/test"
    assert bp._url_prefix == "/test"


def test_blueprint_full_url_prefix_before_registration():
    """Test that full_url_prefix returns None before registration."""
    bp = flask.Blueprint("test", __name__, url_prefix="/test")

    assert bp.full_url_prefix is None


def test_blueprint_full_url_prefix_after_single_registration():
    """Test that full_url_prefix returns the full path after single registration."""
    app = flask.Flask(__name__)
    bp = flask.Blueprint("test", __name__, url_prefix="/test")

    @bp.route("/")
    def index():
        return "test"

    app.register_blueprint(bp, url_prefix="/api")

    assert bp.url_prefix == "/test"
    assert bp.full_url_prefix == "/api/test"
    assert bp.get_registered_url_prefix() == "/api/test"


def test_nested_blueprint_full_url_prefix():
    """Test that nested blueprints get the full URL prefix including parent prefixes."""
    app = flask.Flask(__name__)

    parent = flask.Blueprint("parent", __name__, url_prefix="/parent")
    child = flask.Blueprint("child", __name__, url_prefix="/child")
    grandchild = flask.Blueprint("grandchild", __name__, url_prefix="/grandchild")

    @parent.route("/")
    def parent_index():
        return "parent"

    @child.route("/")
    def child_index():
        return "child"

    @grandchild.route("/")
    def grandchild_index():
        return "grandchild"

    child.register_blueprint(grandchild)
    parent.register_blueprint(child)
    app.register_blueprint(parent, url_prefix="/api")

    assert parent.url_prefix == "/parent"
    assert parent.full_url_prefix == "/api/parent"

    assert child.url_prefix == "/child"
    assert child.full_url_prefix == "/api/parent/child"

    assert grandchild.url_prefix == "/grandchild"
    assert grandchild.full_url_prefix == "/api/parent/child/grandchild"


def test_nested_blueprint_url_rules():
    """Test that nested blueprints have correct URL rules."""
    app = flask.Flask(__name__)

    parent = flask.Blueprint("parent", __name__, url_prefix="/parent")
    child = flask.Blueprint("child", __name__, url_prefix="/child")

    @parent.route("/home")
    def parent_home():
        return "parent home"

    @child.route("/home")
    def child_home():
        return "child home"

    parent.register_blueprint(child)
    app.register_blueprint(parent, url_prefix="/api")

    client = app.test_client()

    assert client.get("/api/parent/home").data == b"parent home"
    assert client.get("/api/parent/child/home").data == b"child home"


def test_multiple_registrations():
    """Test behavior when blueprint is registered multiple times."""
    app = flask.Flask(__name__)
    bp = flask.Blueprint("test", __name__, url_prefix="/test")

    @bp.route("/")
    def index():
        return flask.request.endpoint

    app.register_blueprint(bp, url_prefix="/api1")
    app.register_blueprint(bp, name="test2", url_prefix="/api2")

    assert bp.url_prefix == "/test"
    assert bp.full_url_prefix is None
    assert bp.get_registered_url_prefix() is None
    assert bp.get_registered_url_prefix("test") == "/api1/test"
    assert bp.get_registered_url_prefix("test2") == "/api2/test"

    client = app.test_client()
    assert client.get("/api1/test/").data == b"test.index"
    assert client.get("/api2/test/").data == b"test2.index"


def test_get_registered_url_prefix_with_name():
    """Test get_registered_url_prefix with specific name."""
    app = flask.Flask(__name__)
    bp = flask.Blueprint("test", __name__, url_prefix="/test")

    app.register_blueprint(bp, url_prefix="/api")

    assert bp.get_registered_url_prefix("test") == "/api/test"
    assert bp.get_registered_url_prefix("nonexistent") is None


def test_blueprint_without_url_prefix():
    """Test blueprint without initial url_prefix."""
    app = flask.Flask(__name__)
    bp = flask.Blueprint("test", __name__)

    @bp.route("/")
    def index():
        return "test"

    app.register_blueprint(bp, url_prefix="/api")

    assert bp.url_prefix is None
    assert bp.full_url_prefix == "/api"
    assert bp.get_registered_url_prefix() == "/api"


def test_nested_with_partial_prefixes():
    """Test nested blueprints with some missing prefixes."""
    app = flask.Flask(__name__)

    parent = flask.Blueprint("parent", __name__)
    child = flask.Blueprint("child", __name__, url_prefix="/child")
    grandchild = flask.Blueprint("grandchild", __name__)

    @parent.route("/")
    def parent_index():
        return "parent"

    @child.route("/")
    def child_index():
        return "child"

    @grandchild.route("/")
    def grandchild_index():
        return "grandchild"

    child.register_blueprint(grandchild, url_prefix="/gc")
    parent.register_blueprint(child)
    app.register_blueprint(parent, url_prefix="/api")

    assert parent.full_url_prefix == "/api"
    assert child.full_url_prefix == "/api/child"
    assert grandchild.full_url_prefix == "/api/child/gc"

    client = app.test_client()
    assert client.get("/api/").data == b"parent"
    assert client.get("/api/child/").data == b"child"
    assert client.get("/api/child/gc/").data == b"grandchild"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
