import inspect
import logging

import importlib
from django.conf import settings
from rest_framework.settings import import_from_string

from .apps import VersioningPrimeConfig as AppConfig

logger = logging.getLogger()
retrieved_modules = set()


def get_version_index(version):
    return get_allowed_versions().index(version)


def get_allowed_versions():
    return AppConfig.get_allowed_versions()


def get_classes(module):
    """Iterator that returns a list of classes from the module.

    Args:
        module: Python module.

    Yields:
        Classes from the given module.
        class
    """
    if module.__name__ in retrieved_modules:
        return
    retrieved_modules.add(module.__name__)
    for name, obj in inspect.getmembers(module):
        if inspect.ismodule(obj):
            if obj.__name__.startswith(module.__name__):
                for cls in get_classes(obj):
                    yield cls
        elif inspect.isclass(obj):
            if obj.__module__.startswith(module.__name__):
                yield obj


def assert_versioned_mixin(serializer):
    from .mixins import VersionedMixin
    assert issubclass(serializer, VersionedMixin), (
        '{serializer} is trying to be used in a Transformation, but '
        'does not subclass the VersionedMixin.'.format(
            serializer=serializer
        )
    )


def import_base(base, transformation='Unknown'):
    """Import the base of transformation as a serializer or field.

    Args:
        transformation: ``Transformation`` class with this base. (optional)
        base: Fully qualified class name of serializer, field or a specific serializer's field.

    Returns:
        Tuple of the ``Serializer`` or ``Field``. If a ``Serializer`` with a
        specific field, the name of the field will also be returned.
        tuple
    """
    try:
        serializer = import_from_string(base, 'bases')
        assert_versioned_mixin(serializer)
        return serializer, None
    except (ValueError, ImportError):
        parts = base.split('.')
        try:
            serializer_name = '.'.join(parts[:-1])
            field_name = parts[-1]
        except IndexError:
            logger.error(
                '{transformation} has an invalid base: "{base}".\nCould not import '
                'it as a serializer nor field.'.format(
                    transformation=transformation,
                    base=base
                )
            )
            return None, None
        try:
            serializer = import_from_string(serializer_name, 'bases')
            assert_versioned_mixin(serializer)
            return serializer, field_name
        except (ValueError, ImportError):
            logger.error(
                '{transformation} has an invalid base: "{base}".\nCould not import '
                'the serializer "{serializer}" with the field "{field_name}".'.format(
                    transformation=transformation,
                    base=base,
                    serializer=serializer_name,
                    field_name=field_name
                )
            )
            raise
    return None, None


def generate_transformations():
    """Add ``Transformation`` instances to versioned serializers.

    Every subclass of ``Transformation`` has a list of bases. An instance of
    the ``Transformation`` will be added to each of those bases.

    .. note::
        This should only be called once. This is done in ``AppConfig.ready()``.
    """
    from .transformation import Transformation

    for app in settings.INSTALLED_APPS:
        module = importlib.import_module(app)
        for cls in get_classes(module):
            if issubclass(cls, Transformation) and cls != Transformation:
                transformation = cls
                bases = getattr(transformation, 'bases', None)
                version = getattr(transformation, 'version', None)

                if bases is None or version is None:
                    logger.warning(
                        'The transform subclass "{}" does not have a '
                        'version or bases specified.'.format(
                            transformation
                        )
                    )
                    continue

                for base in bases:
                    base, field_name = import_base(base, transformation=transformation)
                    if base is None:
                        continue
                    base.add_transformation(transformation, field_name=field_name)
