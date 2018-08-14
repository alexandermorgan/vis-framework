#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/articulation.py
# Purpose:                Index music21 "articulations" such as staccato
#                         markings.
#
# Copyright (C) 2018, Alexander Morgan
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
.. codeauthor:: Alexander Morgan

Index music21 "articulations" such as staccato markings. This indexer is based
on the expression indexer.

"""

from music21 import articulations
from vis.analyzers import indexer

symbols = {
    # Articulation          Kern representation
    'accent':               '?',
    'bowing':               '?',
    'down bow':             '?',
    'harmonic':             '?',
    'pizzicato':            '?',
    'staccato':             '?',
    'tenuto':               '?',
    'up bow':               '?',
    }

def indexer_func(event):
    """
    Used internally by :class:`ArticulationIndexer`. Inspects
    :class:`~music21.note.Note` and :class:`~music21.note.Rest` and
    returns kern symbols for *all* articulations present, or else NaN.
    This means that more than one character can be returned if a note
    or a rest has more than one music21 articulation associated with it.

    :param event: Note or rest, chords are not yet supported.

    :type event: :class:`music21.note.Note` or :class:`music21.note.Rest`

    :returns: A string consisting of all the kern representations of
        the music21 articulations present. These can later be filtered
        to a single type of articulation if desired. If no articulations
        are present for the note or rest, NaN is returned.

    :rtype: str or float
    """
    if isinstance(event, float): # event is NaN
        return event
    else:
        res = []
        for arti in event.articulation:
            if arti.name in symbols:
                res.append(symbols[arti.name])
        if res:
            return ''.join(res)
        return float('nan')


class ArticulationIndexer(indexer.Indexer):
    """
    Index :class:`~music21.articulations`.
    Finds :class:`~music21.articulations`s.

    **Example:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('pathnameToScore.xml')
    >>> ip.get_data('articulation')

    """
    default_settings = {'articulation': 'all'}
    required_score_type = 'pandas.DataFrame'

    def __init__(self, score, settings=None):
        """
        :param score: A dataframe of the note, rest, and chord objects
            in a piece.

        :type score: pandas Dataframe

        :param settings: Settings are not currently implemented, but
            could potentially allow for the filtering of unwanted
            articulations. For example, if you're just looking for
            tenutos, a setting could filter out all the other
            articulations that would otherwise be included in the
            results.

        :type settings: Dictionary

        :raises: :exc:`RuntimeError` if ``score`` is not a pandas
            Dataframe.

        """
        self._settings = ArticulationIndexer.default_settings.copy()
        super(ArticulationIndexer, self).__init__(score, self._settings)
        self._types = ('Note', 'Rest')
        self._indexer_func = indexer_func
