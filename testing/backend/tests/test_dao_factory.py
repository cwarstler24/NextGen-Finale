"""
Tests for DAOFactory class in DAOfactory.py.

DAOs can be instantiated safely — AbstractDAO.__init__ only stores table_name,
primary_key, and a logger; no DB connection is made.
"""
import pytest
from main.backend.DAOfactory import DAOFactory


@pytest.fixture(autouse=True)
def clean_factory():
    """Ensure DAOFactory is empty before and after every test."""
    DAOFactory.reset()
    yield
    DAOFactory.reset()


# ==================== list_active ====================

class TestListActive:
    def test_empty_when_no_daos_created(self):
        assert DAOFactory.list_active() == []

    def test_reflects_created_daos(self):
        DAOFactory.create_dao("BunTypeDAO")
        DAOFactory.create_dao("PattyTypeDAO")
        active = DAOFactory.list_active()
        assert "BunTypeDAO" in active
        assert "PattyTypeDAO" in active

    def test_returns_copy_list(self):
        """list_active() returns a list, not the internal dict."""
        result = DAOFactory.list_active()
        assert isinstance(result, list)


# ==================== create_dao ====================

class TestCreateDao:
    def test_returns_dao_instance(self):
        dao = DAOFactory.create_dao("CustomerDAO")
        assert dao is not None

    def test_instance_is_stored(self):
        dao = DAOFactory.create_dao("CustomerDAO")
        assert DAOFactory.get_dao("CustomerDAO") is dao

    def test_creates_each_registered_type(self):
        types = [
            "CustomerDAO", "OrderDAO", "OrderItemDAO", "BurgerItemDAO",
            "BurgerItemToppingDAO", "FryItemDAO", "BunTypeDAO",
            "PattyTypeDAO", "ToppingDAO", "FryTypeDAO", "FrySizeDAO",
            "FrySeasoningDAO",
        ]
        for name in types:
            dao = DAOFactory.create_dao(name)
            assert dao is not None
            # clean up between each so list stays manageable
            DAOFactory.reset(name)

    def test_raises_if_dao_already_exists(self):
        DAOFactory.create_dao("BunTypeDAO")
        with pytest.raises(RuntimeError, match="already created"):
            DAOFactory.create_dao("BunTypeDAO")

    def test_raises_for_unknown_dao_name(self):
        with pytest.raises(RuntimeError, match="has not been registered"):
            DAOFactory.create_dao("MadeUpDAO")

    def test_raises_for_empty_string(self):
        with pytest.raises(RuntimeError):
            DAOFactory.create_dao("")


# ==================== get_dao ====================

class TestGetDao:
    def test_raises_if_dao_not_created(self):
        with pytest.raises(RuntimeError, match="not yet created"):
            DAOFactory.get_dao("CustomerDAO")

    def test_returns_same_instance_each_time(self):
        first = DAOFactory.create_dao("FrySizeDAO")
        assert DAOFactory.get_dao("FrySizeDAO") is first
        assert DAOFactory.get_dao("FrySizeDAO") is first


# ==================== get_or_create_dao ====================

class TestGetOrCreateDao:
    def test_creates_when_not_present(self):
        dao = DAOFactory.get_or_create_dao("ToppingDAO")
        assert dao is not None

    def test_returns_existing_instance(self):
        created = DAOFactory.create_dao("FryTypeDAO")
        fetched = DAOFactory.get_or_create_dao("FryTypeDAO")
        assert fetched is created

    def test_calling_twice_returns_same_object(self):
        first = DAOFactory.get_or_create_dao("OrderDAO")
        second = DAOFactory.get_or_create_dao("OrderDAO")
        assert first is second


# ==================== reset ====================

class TestReset:
    def test_reset_specific_removes_only_that_dao(self):
        DAOFactory.create_dao("BunTypeDAO")
        DAOFactory.create_dao("PattyTypeDAO")
        DAOFactory.reset("BunTypeDAO")
        assert "BunTypeDAO" not in DAOFactory.list_active()
        assert "PattyTypeDAO" in DAOFactory.list_active()

    def test_reset_all_clears_everything(self):
        DAOFactory.create_dao("BunTypeDAO")
        DAOFactory.create_dao("ToppingDAO")
        DAOFactory.reset()
        assert DAOFactory.list_active() == []

    def test_reset_nonexistent_does_not_raise(self):
        """pop() on missing key is safe."""
        DAOFactory.reset("NonExistentDAO")  # should not raise

    def test_after_reset_can_create_again(self):
        DAOFactory.create_dao("FrySeasoningDAO")
        DAOFactory.reset("FrySeasoningDAO")
        dao = DAOFactory.create_dao("FrySeasoningDAO")
        assert dao is not None
