"""Defines immutal global constant
From: http://code.activestate.com/recipes/65207-constants-in-python/?in=user-97991
"""
import sys

class _const(object):
    """Immutable constant"""
    class ConstError(TypeError):
        """Thrown when trying to change constant"""
        pass
    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't rebind const(%s)" % name
        self.__dict__[name] = value

sys.modules[__name__] = _const()
