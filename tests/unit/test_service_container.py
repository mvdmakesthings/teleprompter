"""Unit tests for ServiceContainer."""

from unittest.mock import Mock

import pytest

from src.teleprompter.core.container import ServiceContainer
from src.teleprompter.core.exceptions import ServiceNotFoundError


class TestServiceContainer:
    """Test the ServiceContainer class."""

    @pytest.fixture
    def container(self):
        """Create a ServiceContainer instance."""
        return ServiceContainer()

    def test_initialization(self, container):
        """Test container initialization."""
        assert container._services == {}
        assert container._factories == {}
        assert container._singletons == {}

    def test_register_instance(self, container):
        """Test registering an instance."""
        # Create a mock service
        service = Mock()

        # Register it as singleton (instances should be singletons)
        container.register_instance(Mock, service)

        # Resolve it
        resolved = container.get(Mock)
        assert resolved is service

    def test_register_class_as_singleton(self, container):
        """Test registering a class as singleton."""

        class TestService:
            pass

        # Register class
        container.register(TestService, TestService)

        # Resolve multiple times - should get same instance
        instance1 = container.get(TestService)
        instance2 = container.get(TestService)

        assert instance1 is instance2
        assert isinstance(instance1, TestService)

    def test_register_class_not_singleton(self, container):
        """Test registering a class not as singleton."""

        class TestService:
            pass

        # Register class
        container.register(TestService, TestService, singleton=False)

        # Resolve multiple times - should get different instances
        instance1 = container.get(TestService)
        instance2 = container.get(TestService)

        assert instance1 is not instance2
        assert isinstance(instance1, TestService)
        assert isinstance(instance2, TestService)

    def test_register_factory(self, container):
        """Test registering a factory function."""
        # Create a factory
        counter = 0

        def factory():
            nonlocal counter
            counter += 1
            return f"instance_{counter}"

        # Register factory
        container.register_factory(str, factory)

        # Resolve multiple times - factories create singletons
        result1 = container.get(str)
        result2 = container.get(str)

        assert result1 == "instance_1"
        assert result2 == "instance_1"  # Same instance
        assert result1 is result2

    def test_resolve_unregistered_type(self, container):
        """Test resolving unregistered type raises error."""

        class UnregisteredService:
            pass

        with pytest.raises(ServiceNotFoundError):
            container.get(UnregisteredService)

    def test_has_registered(self, container):
        """Test checking if service is registered."""

        class TestService:
            pass

        # Not registered yet
        assert not container.has(TestService)

        # Register it
        container.register(TestService, TestService)

        # Now it's registered
        assert container.has(TestService)

    def test_clear(self, container):
        """Test clearing all registrations."""
        # Register some services
        container.register(str, "test")
        container.register(int, 42)

        assert container.has(str)
        assert container.has(int)

        # Clear all
        container.clear()

        assert not container.has(str)
        assert not container.has(int)
