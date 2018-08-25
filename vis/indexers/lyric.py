#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           Vizitka
# Program Description:    Helps analyze music with computers and convert
#                         files from various music-encoding formats to
#                         kern.
#
# Filename:               analyzers/indexers/lyric.py
# Purpose:                Index the lyrics in a piece.
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

Index the lyrics in a piece.
"""

from vis.indexers import indexer

def indexer_func(event):
    """
    :param event: music21 note, rest, or chord.
    :type event: :class:`music21.note.Note`, :class:`music21.note.Rest`, or
        :class:`music21.chord.Chord`

    :returns: A string of the lyrics for a given note, rest, or chord,
        otherwise a NaN is returned.

    :rtype: str or float
    """
    if isinstance(event, float): # event is NaN
        return event
    elif event.lyric: # if the event has no lyrics, it is a None which is False
        return event.lyric
    return float('nan')


class LyricIndexer(indexer.Indexer):
    """
    Index lyrics on notes, rests, and chords.
    Finds the text strings of lyrics.

    **Example:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('pathnameToScore.xml')
    >>> ip.get('lyric')

    """
    required_score_type = 'pandas.DataFrame'

    def __init__(self, score, settings=None):
        """
        :param score: A dataframe of the note, rest, and chord objects
            in a piece.
        :type score: pandas Dataframe

        :raises: :exc:`RuntimeError` if ``score`` is not a pandas
            Dataframe.

        """
        self._settings = LyricIndexer.default_settings.copy()
        super(LyricIndexer, self).__init__(score, self._settings)
        self._types = ('Note', 'Rest')
        self._indexer_func = indexer_func

    # NB: this indexer inherits its run method from indexer.py
