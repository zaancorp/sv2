#!/usr/bin/env python
"""Singleton metaclass for restricting a class to a single instance."""


class Singleton(type):
    """Metaclass that enforces the singleton pattern: at most one instance per class."""

    def __init__(self, name, bases, dic):
        """Initialise the metaclass and set the instance holder to None."""
        super(Singleton, self).__init__(name, bases, dic)
        self.instance = None

    def __call__(self, *args, **kw):
        """
        Return the existing instance, or create and store one if none exists yet.

        @return: The single instance of the class.
        """
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kw)
        return self.instance
