from typing import List, Optional, Type

import discord


class ViewCollector:
    """
    A utility class to manage multiple Discord UI Views. This class allows
    you to add, remove, retrieve, and clean up views efficiently. Views are
    stored in an internal list, and the class provides various methods for
    managing and querying them.

    Attributes:
        _views (List[discord.ui.View]): A private list to store the added views.
    """
    
    _views: List[discord.ui.View]

    def __init__(self) -> None:
        self._views = []

    def add_view(self, view: discord.ui.View) -> None:
        self._views.append(view)

    def remove_view(self, view):
        if view in self.views:
            self.views.remove(view)

    def cleanup(self):
        for view in self.views:
            view.stop()
        self.views.clear()

    def get_view(
        self,
        *,
        cls: Type[discord.ui.View] = None,
        name: str = None,
        **attributes
    ) -> Optional[discord.ui.View]:
        """
        Finds the first matching view by class and attributes.
        :param cls: The class the view should belong to (optional).
        :param attributes: Attributes to filter the views.
        """
        for view in self._views:
            if cls and not isinstance(view, cls):
                continue
            if name and view.__class__.__name__ != name:
                continue
            if all(
                getattr(view, attr, None) == value
                for attr, value in attributes.items()
            ):
                return view
        return None

    def get_views(
        self,
        *,
        cls: Type[discord.ui.View] = None,
        name: str = None,
        **attributes
    ) -> Optional[List[discord.ui.View]]:
        """
        Finds all views matching the class and attributes.
        :param cls: The class the views should belong to (optional).
        :param attributes: Attributes to filter the views.
        """
        result = []
        for view in self._views:
            if cls and not isinstance(view, cls):
                continue
            if name and view.__class__.__name__ != name:
                continue
            if all(
                getattr(view, attr, None) == value
                for attr, value in attributes.items()
            ):
                result.append(view)
        return result
