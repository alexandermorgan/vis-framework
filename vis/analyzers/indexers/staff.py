#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/staff.py
# Purpose:                Indexers for staff elements.
#
# Copyright (C) 2018 Alexander Morgan
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
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
.. codeauthor:: Alexander Morgan

Indexers for staff elements.
"""

# disable "string statement has no effect" warning---they do have an effect
# with Sphinx!
# pylint: disable=W0105

import pandas
from vis.analyzers import indexer

def ind_func(event):
    """
    Handles all music21 objects types and returns Humdrum-format string for
    staff objects, namely time signatures, keys, and clefs.

    :param event: A music21 object.
    :type event: A music21 object or a float('nan').

    :returns: The Humdrum representation string for the staff element.
    :rtype: string or float('nan').
    """
    if 'TimeSignature' in event.classes:
        return '*M' + event.ratioString
    elif 'Key' in event.classes or 'KeySignature' in event.classes:
        armure = ['*k[']
        [armure.append(p.name.lower()) for p in event.alteredPitches]
        armure.append(']')
        return ''.join(armure)
    elif 'Clef' in event.classes:
        clef = ['*clef', event.sign, str(event.line)]
        if event.octaveChange == 0:
            pass
        elif event.octaveChange == -1:
            clef.insert(2, 'v')
        elif event.octaveChange == 1:
            clef.insert(2, 'va')
        return ''.join(clef)

    return float('nan')


class StaffIndexer(indexer.Indexer):
    """
    Make an index of the staff elements in a piece including time signatures,
    keys, and clefs.
    """

    required_score_type = 'pandas.Series' # actually a list of series.

    def __init__(self, score):
        """
        :param score: list of music21 parts as pandas.Series
        :type score: list of :class:`pandas.Series` of music21 objects
        """
        super(StaffIndexer, self).__init__(score, None)
        self._indexer_func = ind_func

    def run(self):
        """
        Make a new index of the staff elements in the piece. It's no problem
        if the parts change time signatures, etc. at different times.

        :returns: The Humdrum-format staff elements in a piece.
        :rtype: :class:`pandas.DataFrame`, or None if there are no parts.
        """
        if len(self._score) == 0: # if there are no parts
            return None
        post = [part.apply(staff_ind_func).dropna() for part in self._score]
        return pandas.concat(post, axis=1)
