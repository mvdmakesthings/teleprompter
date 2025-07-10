"""Dependency injection container for the teleprompter application.

This module provides a simple dependency injection container to manage
dependencies and promote loose coupling between components.
"""

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

T = TypeVar("T")


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not found in the container."""

    pass


class ServiceContainer:
    """Simple dependency injection container."""

    def __init__(self):
        self._services: dict[type, Any] = {}
        self._factories: dict[type, Callable[[], Any]] = {}
        self._singletons: dict[type, Any] = {}

    def register(
        self,
        interface: type[T],
        implementation: type[T] | T | Callable[[], T],
        singleton: bool = True,
    ) -> None:
        """Register a service in the container.

        Args:
            interface: The interface/protocol type
            implementation: The implementation class, instance, or factory function
            singleton: Whether to create a single instance (default: True)
        """
        if inspect.isclass(implementation):
            # Register class
            if singleton:
                self._factories[interface] = lambda: self._create_instance(
                    implementation
                )
            else:
                self._services[interface] = implementation
        elif callable(implementation) and not isinstance(implementation, type):
            # Register factory function
            self._factories[interface] = implementation
        else:
            # Register instance
            self._singletons[interface] = implementation

    def register_instance(self, interface: type[T], instance: T) -> None:
        """Register a pre-created instance."""
        self._singletons[interface] = instance

    def register_factory(self, interface: type[T], factory: Callable[[], T]) -> None:
        """Register a factory function."""
        self._factories[interface] = factory

    def get(self, interface: type[T]) -> T:
        """Retrieve a service from the container."""
        # Check singletons first
        if interface in self._singletons:
            return self._singletons[interface]

        # Check factories
        if interface in self._factories:
            if interface not in self._singletons:
                self._singletons[interface] = self._factories[interface]()
            return self._singletons[interface]

        # Check services (non-singleton)
        if interface in self._services:
            return self._create_instance(self._services[interface])

        raise ServiceNotFoundError(
            f"Service {interface.__name__} not found in container"
        )

    def has(self, interface: type) -> bool:
        """Check if a service is registered."""
        return (
            interface in self._services
            or interface in self._factories
            or interface in self._singletons
        )

    def _create_instance(self, cls: type[T]) -> T:
        """Create an instance with dependency injection."""
        # Get constructor signature
        sig = inspect.signature(cls.__init__)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # Get type annotation
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                continue

            # Try to resolve dependency
            if self.has(param_type):
                kwargs[param_name] = self.get(param_type)
            elif param.default != inspect.Parameter.empty:
                # Use default value
                kwargs[param_name] = param.default
            else:
                # Skip if we can't resolve and no default
                pass

        return cls(**kwargs)

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()


# Global container instance
_container = ServiceContainer()


def get_container() -> ServiceContainer:
    """Get the global container instance."""
    return _container


def inject(func: Callable) -> Callable:
    """Decorator for dependency injection in functions/methods."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        container = get_container()

        # Inject missing parameters
        for param_name, param in sig.parameters.items():
            if param_name in kwargs:
                continue

            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                continue

            if container.has(param_type):
                kwargs[param_name] = container.get(param_type)

        return func(*args, **kwargs)

    return wrapper


class Injectable:
    """Base class for classes that support dependency injection."""

    def __init_subclass__(cls, **kwargs):
        """Automatically register subclasses in the container."""
        super().__init_subclass__(**kwargs)

        # Check if class has an interface attribute
        if hasattr(cls, "__interface__"):
            get_container().register(cls.__interface__, cls)


def configure_container() -> ServiceContainer:
    """Configure the dependency injection container with all services."""
    container = get_container()
    container.clear()

    # Import implementations
    from .file_manager import FileManager
    from .markdown_parser import MarkdownParser
    from .protocols import (
        ContentParserProtocol,
        FileLoaderProtocol,
        SettingsStorageProtocol,
        StyleProviderProtocol,
    )
    from .settings_manager import SettingsManager
    from .style_manager import StyleManager

    # Register services
    container.register(FileLoaderProtocol, FileManager)
    container.register(ContentParserProtocol, MarkdownParser)
    container.register(SettingsStorageProtocol, SettingsManager)
    container.register(StyleProviderProtocol, StyleManager)

    # Also register concrete implementations for backwards compatibility
    container.register(StyleManager, StyleManager)

    return container
