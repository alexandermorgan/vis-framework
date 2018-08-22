#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers and convert
#                         files from various music-encoding formats to
#                         kern.
#
# Filename:               analyzers/indexers/viz2hum.py
# Purpose:                Create a Humdrum-format score.
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

Create a Humdrum-format kern score.
"""

import pandas as pd
import pdb
from vis.analyzers import indexer
from music21 import chord
from vis.analyzers.indexers.articulation import indexer_func as artIF
from vis.analyzers.indexers.articulation import symbols
from vis.analyzers.indexers.expression import indexer_func as expIF
from vis.analyzers.indexers.meter import tie_ind_func as tieIF


# Used to memoize hDurIF results. Start with some tuplet durations since I
# currently have a function that can handle these.
recip = {2.66667: '3%2', # two thirds of a whole note
         1.33333: '3', # one third of a whole note
         .66667: '3%4'}

def hDurIF(event):
    """Works on notes, rests, and chords. Returns a single value for chords.
    Returns a duration string in the Humdrum format. This should probably be
    replaced with a subprocess call to recip because it will miss most tricky
    times like almost any tuple or ternary stuff. Uses memoization. """
    if isinstance(event, float):
        return event

    rounded = float(round(event.quarterLength, 5))
    if rounded not in recip:
        dots = event.duration.dots
        if dots == 0:
            ret = str(int(4/event.quarterLength))
        elif dots == 1:
            ret = str(int(6/event.quarterLength)) + '.'
        elif dots == 2:
            ret = str(int(7/event.quarterLength)) + '..'
        recip[rounded] = ret
    return recip[rounded]

def hNRIF(nr):
    """  Only processes notes and rests, so for chords you should call this
    function on each of the pitches in the chord. Returns Humdrum-format for
    the note or rest's pitch name or 'r' for rest.
    """
    if hasattr(nr, 'isRest') and nr.isRest:
        post = 'r'
    elif nr.octave > 3: # nr is middle C or higher
        post = nr.name[0].lower() * (-1*(3-nr.octave)) + nr.name[1:]
    else: # nr is below middle C
        post = (nr.name[0] * (4-nr.octave)) + nr.name[1:]

    return post

def stemIF(event):
    """Returns Humdrum-style stem-direction token if the stem direction is
    specified."""
    if event.isRest or event.stemDirection == 'unspecified':
        return None
    elif event.stemDirection == 'up':
        return '/'
    elif event.stemDirection == 'down':
        return '\\'

ind_funcs = [hDurIF,
             hNRIF,
             expIF,
             artIF,
             tieIF,
             ]

def indexer_func(event):
    """
    Used internally by :class:`Viz2HumIndexer`. Creates a Humdrum-format kern
    score of an indexed piece.

    :param event: music21 note, rest, or chord.
    :type event: :class:`music21.note.Note`, :class:`music21.note.Rest`, or
        :class:`music21.chord.Chord`

    :returns: A Humdrum-style kern score as a tab separated spreadsheet.
    :rtype: pandas.DataFrame
    """
    if isinstance(event, float): # event is NaN
        return event

    # For notes and rests:
    elif 'Note' in event.classes or 'Rest' in event.classes:
        res = [func(event) for func in ind_funcs if isinstance(func(event), str)]

    # Handle special case of chords
    elif isinstance(event, chord.Chord):
        outer_temp = []
        for p in event.pitches:
            temp = [hDurIF(event),
                    hNRIF(p),
                    stemIF(event),
                    expIF(event),
                    artIF(event),
                    tieIF(event),
                    ', '
                    ]
            outer_temp.extend(temp)
        outer_temp.pop(-1) # get rid of the last comma and space
        res = [s for s in outer_temp if isinstance(s, str)]

    return ''.join(res)



class Viz2HumIndexer(indexer.Indexer):
    """
    Index all musical events and metadata.
    Creates a Humdrum-style kern score.

    **Example:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('pathnameToScore.xml')
    >>> ip.get_data('viz2hum')

    """
    required_score_type = 'pandas.DataFrame'

    def __init__(self, score, settings=None):
        """
        :param score: 2-tuple of measure and m21_nrc_objs dataframes
        :type score: 2-tuple of pandas.DataFrames

        :raises: :exc:`RuntimeError` if ``score`` is not a pandas
            Dataframe.

        """
        self._settings = Viz2HumIndexer.default_settings.copy()
        super(Viz2HumIndexer, self).__init__(score, self._settings)
        self._types = ('Note', 'Rest', 'Chord')
        self._indexer_func = indexer_func

    def run(self):
        """
        Manage the primary indexing and also the secondary addition of
        metadata, comments, etc. The first df in self._score is the measures,
        the second one is the note, rest, and chord objects.
        """
        num_cols = self._score[0].shape[1]
        col_indx = range(num_cols)
        dfs = [df for df in self._score[:5]]
        # Index the note, rest and chord objects.
        dfs[4] = dfs[4].applymap(indexer_func) # nrc objects
        # Reverse the order of the parts.
        dfs[4] = pd.concat([dfs[4].iloc[:,i] for i in col_indx], axis=1)

        for i, df in enumerate(dfs):
            # drop the column names:
            df.columns = col_indx
            # Give a name to the existing index
            df.index.name = 'Offset'
            # Create a new index, first as a column
            df['Order'] = i
            # Make the "Order" column part of the MultiIndex
            df.set_index('Order', append=True, inplace=True)

        # Merge and sort dfs, breaking offset ties with "Order" from above.
        post = pd.concat(dfs)
        post.sort_index(inplace=True)
        # Reverse the order of the parts:
        post = pd.concat([post.iloc[:,x] for x in reversed(col_indx)], axis=1, ignore_index=True)

        # Make the empty cells into period strings.
        post.fillna('.', inplace=True)

        # Prepare the fields at the beginning of the file.
        vizmd = self._score[6] # Vizitka metadata
        m21md = self._score[7] # music21 metadata

        com, enc, eed = [None]*3
        if hasattr(m21md, 'contributors'):
            for c in m21md.contributors:
                if c.role in ('composer', 'attributed composer') and com is None:
                    com = '!!!COM: ' + c.name
                elif c.role == 'electronic encoder':
                    enc = '!!!ENC: ' + c.name
                elif c.role == 'electronic editor':
                    eed = '!!!EED: ' + c.name

        ttl = '!!!OPR: ' + vizmd['title'] if vizmd['title'] else None
        vcs = '!!!voices: ' + str(num_cols)
        head_data = pd.Series((com, ttl, vcs)).dropna()
        header = [pd.Series(('**kern', '*staff'+str(i+1),
                             #part names
                             '*I"'+vizmd['parts'][i] if vizmd['parts'][i][:5] != 'Part ' else None,
                              #part-name abbreviations:
                             "*I'"+vizmd['parts'][i][0] if vizmd['parts'][i][:5] != 'Part ' else None,
                             )).dropna() for i in col_indx]
        header = pd.concat(header, axis=1)

        # final barlines and end of kern tokens
        footer = pd.concat([pd.Series(['==', '*_'])]*num_cols, axis=1)
        # metadata at the end of a file
        tail_data = pd.Series(('!!!RDF**kern: l=long note in original notation', # meaning of l character
                     '!!!RDF**kern: i=editorial accidental', # meaning of i character
                     enc,
                     eed,
                     '!!!ONB: Converted to Humdrum using Vizitka', # Vizitka conversion stamp
                     None if not hasattr(m21md, 'copyright') or m21md.copyright is None else '!!!YEC: '+m21md.copyright,
                     None if not hasattr(m21md, 'date') or m21md.date == 'None' else '!!!DAT: '+m21md.date)).dropna()
        # Assemble all the chunks and get rid of the row index.
        res = pd.concat((head_data, header, post, footer, tail_data), ignore_index=True)

        return res
