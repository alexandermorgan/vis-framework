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
from vizitka.indexers import indexer
import pdb

nan = float('nan')

def clef_ind_func(event):
    """
    Handles all music21 objects types and returns Humdrum-format string for
    the clefs.

    :param event: A music21 object.
    :type event: A music21 object or a float('nan').

    :returns: The Humdrum representation string for the clefs.
    :rtype: string or float('nan').
    """
    if 'Clef' in event.classes:
        clef = ['*clef', event.sign, str(event.line)]
        if event.octaveChange == 0:
            pass
        elif event.octaveChange == -1:
            clef.insert(2, 'v')
        elif event.octaveChange == 1:
            clef.insert(2, 'va')
        return ''.join(clef)

    return nan

def key_signature_ind_func(event):
    """
    Handles all music21 objects types and returns Humdrum-format string for
    key signatures.

    :param event: A music21 object.
    :type event: A music21 object or a float('nan').

    :returns: The Humdrum representation string for the key signature.
    :rtype: string or float('nan').
    """
    if 'Key' in event.classes or 'KeySignature' in event.classes:
        armure = ['*k[']
        [armure.append(p.name.lower()) for p in event.alteredPitches]
        armure.append(']')
        return ''.join(armure)

    return nan



class ClefIndexer(indexer.Indexer):
    """
    Make an index of the clefs in a piece.

    **Example:**
    from vizitka.models.indexed_piece import Importer
    ip = Importer('pathnameToScore.xml')
    ip.get('cl')
    """

    required_score_type = 'pandas.Series' # actually a list of series

    def __init__(self, score):
        """
        :param score: list of music21 parts as pandas.Series
        :type score: list of :class:`pandas.Series` of music21 objects
        """
        super(ClefIndexer, self).__init__(score, None)
        self._indexer_func = clef_ind_func

    def run(self):
        """
        Make a new index of the clefs in the piece. It's no problem
        if the parts change clefs at different times.

        :returns: The Humdrum-formated clefs in a piece.
        :rtype: :class:`pandas.DataFrame`, or None if there are no parts.
        """
        if len(self._score) == 0: # if there are no parts
            return None
        post = [part.apply(self._indexer_func).dropna() for part in self._score]
        ret = pandas.concat(post, axis=1).dropna(how='all')
        mi = pandas.MultiIndex.from_product((('Clef',), ret.columns),
                                            names=('Indexer', 'Parts'))
        ret.columns = mi
        return ret.fillna('*')


class KeySignatureIndexer(indexer.Indexer):
    """
    Make an index of the key signatures in a piece.

    **Example:**
    from vizitka.models.indexed_piece import Importer
    ip = Importer('pathnameToScore.xml')
    ip.get('ks')
    """

    required_score_type = 'pandas.Series' # actually a list of series

    def __init__(self, score):
        """
        :param score: list of music21 parts as pandas.Series
        :type score: list of :class:`pandas.Series` of music21 objects
        """
        super(KeySignatureIndexer, self).__init__(score, None)
        self._indexer_func = key_signature_ind_func

    def run(self):
        """
        Make a new index of the key signatures in the piece. It's no problem
        if the parts change key signatures at different times.

        :returns: The Humdrum-formated key signatures in a piece.
        :rtype: :class:`pandas.DataFrame`, or None if there are no parts.
        """
        if len(self._score) == 0: # if there are no parts
            return None
        post = [part.apply(self._indexer_func).dropna() for part in self._score]
        ret = pandas.concat(post, axis=1).dropna(how='all')
        mi = pandas.MultiIndex.from_product((('KeySignature',), ret.columns),
                                            names=('Indexer', 'Parts'))
        ret.columns = mi
        return ret.fillna('*')
