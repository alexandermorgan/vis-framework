#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/expression.py
# Purpose:                Index music21 "expressions" such as fermatas.
#
# Copyright (C) 2013, 2014, 2016, 2018 Christopher Antila, Ryan Bannon,
# Alexander Morgan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------- #
"""
.. codeauthor:: Ryan Bannon <ryan.bannon@gmail.com>
.. codeauthor:: Alexander Morgan

Index music21 "expressions" such as fermatas.

"""

import six
from music21 import expressions
from vis.analyzers import indexer

def indexer_func(event):
    """
    Used internally by :class:`FermataIndexer`. Inspects

    :class:`~music21.note.Note` and :class:`~music21.note.Rest` and
        returns ``u'Fermata'`` if a fermata is associated, else NaN.

    :param event: An iterable (nominally a :class:`~pandas.Series`) with
        an object to convert. Only the first object in the iterable is
        processed.

    :type event: iterable of :class:`music21.note.Note` or
        :class:`music21.note.Rest`

    :returns: If the first object in the list is a contains a
        :class:`~music21.expressions.Fermata`, string ``u'Fermata'``
        is returned. Else, NaN.

    :rtype: str
    """

    if isinstance(event, float): # event is NaN
        return event
    for expr in event.expressions:
        if isinstance(expr, self._expr_type):
            return self._expr_str


class ExpressionIndexer(indexer.Indexer):
    """
    Index :class:`~music21.expressions`.

    Finds :class:`~music21.expressions`s.

    **Example:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('pathnameToScore.xml')
    >>> ip.get_data('expression')

    """
    default_settings = {'expression': 'fermata'}
    supported_expressions = ('fermata',)
    required_score_type = 'pandas.DataFrame'
    expr_types = {'fermata': (expressions.Fermata, ".)")}

    _UNSUPPORTED_EXPRESSION = "This is not a music21 expression."

    def __init__(self, score, settings=None):
        """
        :param score: A dataframe of the note, rest, and chord objects
            in a piece.

        :type score: pandas Dataframe

        :param settings: This indexer does not have any settings, so
            this is just a place holder.

        :type settings: None

        :raises: :exc:`RuntimeError` if ``score`` is not a pandas
            Dataframe.

        """
        if settings is None:
            self._settings = default_settings
        elif ('expression' in settings and
              settings[expression] not in supported_expressions):
            raise RuntimeError(ExpressionIndexer._UNSUPPORTED_EXPRESSION)
        else:
            self._settings = default_settings.copy().update(settings)
        super(ExpressionIndexer, self).__init__(score, self._settings)
        self._types = ('Note', 'Rest', 'Chord')
        self._expr_type = expr_types[self._settings['expression'][0]]
        self._expr_str = expr_types[self._settings['expression'][1]]
        self._indexer_func = indexer_func
