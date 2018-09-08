#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/meter.py
# Purpose:                Indexers for metric concerns.
#
# Copyright (C) 2013-2016 Christopher Antila, Alexander Morgan
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
.. codeauthor:: Christopher Antila <christopher@antila.ca>
.. codeauthor:: Alexander Morgan

Indexers for metric concerns.
"""

# disable "string statement has no effect" warning---they do have an effect
# with Sphinx!
# pylint: disable=W0105

import pandas
from vizitka.indexers import indexer
import pdb

tie_types = {'start': '[', 'continue': '_', 'stop': ']'}
nan = float('nan')

def beatstrength_ind_func(event):
    """
    Used internally by :class:`NoteBeatStrengthIndexer`. Convert
    :class:`~music21.note.Note` and :class:`~music21.note.Rest` objects
    into a string.

    :param event: A music21 note, rest, or chord object which get queried for its beat strength.
    :type event: A music21 note, rest, or chord object or NaN.

    :returns: The :attr:`~music21.base.Music21Object.beatStrength` of the event which is dependent
        on the prevailing time signature.
    :rtype: float
    """
    if isinstance(event, float):
        return event
    return event.beatStrength

def measure_ind_func(event):
    """
    The function that indexes the measure numbers of each part in a piece. Unlike most other
    indexers, this one returns int values. Measure numbering starts from 1 unless there is a pick-up
    measure which gets the number 0. This can handle changes in time signature without problems.

    :param event: A music21 measure object which gets queried for its "number" attribute.
    :type event: A music21 measure object or NaN.

    :returns: The number attribute of the passed music21 measure.
    :rtype: int
    """
    if isinstance(event, float):
        return event
    return event.number

def tie_ind_func(event):
    """
    Handles music21 note, rest, or chord objects and identifies what type of
    tie they have, if any.

    :param event: A music21 note, rest, or chord object.
    :type event: A music21 object or a float('nan').

    :returns: The Humdrum representation of the event's tie type, or NaN if
        if there isn't one or if the object was a NaN to begin withself.
    :rtype: string or float('nan').
    """
    if isinstance(event, float):
        return event
    elif hasattr(event, 'tie') and event.tie is not None:
        return(tie_types[event.tie.type])
    else:
        return float('nan')

def time_signature_ind_func(event):
    """
    Handles all music21 objects types and returns Humdrum-format string for
    time signatures.

    :param event: A music21 object.
    :type event: A music21 object or a float('nan').

    :returns: The Humdrum representation string for the staff element.
    :rtype: string or float('nan').
    """
    if 'TimeSignature' in event.classes:
        return '*M' + event.ratioString
    return nan



class NoteBeatStrengthIndexer(indexer.Indexer):
    """
    Make an index of the :attr:`~music21.base.Music21Object.beatStrength` for all :class:`Note`,
    :class:`Rest`, and :class:`Chord` objects.

    .. note:: Unlike nearly all other indexers, this indexer returns a :class:`Series` of ``float``
    objects rather than ``unicode`` objects.

    **Example:**
    from vizitka.models.indexed_piece import Importer
    ip = Importer('pathnameToScore.xml')
    ip.get('beat_strength')
    """

    required_score_type = 'pandas.DataFrame'

    def __init__(self, score):
        """
        :param score: A dataframe of the note, rest, and chord objects in a piece.
        :type score: pandas Dataframe

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        """

        super(NoteBeatStrengthIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest', 'Chord')
        self._indexer_func = beatstrength_ind_func

    # NB: This indexer inherits its run() method from indexer.py


class DurationIndexer(indexer.Indexer):
    """
    Make an index of the durations of all :class:`Note`, :class:`Rest`, and :class:`Chord` objects.
    These are calculated based on the difference in index positions of consecutive events.

    .. note:: Unlike nearly all other indexers, this indexer returns a :class:`Series` of ``float``
    objects rather than ``unicode`` objects. Also unlike most other indexers, this indexer does not
    have an indexer func.

    **Example:**
    from vizitka.models.indexed_piece import Importer
    ip = Importer('pathnameToScore.xml')
    ip.get('duration')
    """

    required_score_type = 'pandas.DataFrame'

    def __init__(self, score, part_streams):
        """
        :param score: A :class:`pandas.DataFrame` of the note, rest, and chord objects in a piece.
        :type score: :class:`pandas.DataFrame`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        """

        super(DurationIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest', 'Chord')
        self._part_streams = part_streams

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices of the durations of each note or rest event in a score. Note that
            each item is a float, rather than the usual basestring.
        :rtype: :class:`pandas.DataFrame`
        """
        if len(self._score) == 0: # if there are no notes or rests
            result = self._score.copy()
        else:
            durations = []
            for part in range(len(self._score.columns)):
                indx = self._score.iloc[:, part].dropna().index
                new = indx.insert(len(indx), self._part_streams[part].highestTime)
                durations.append(pandas.Series((new[1:].values - indx.values), index=indx))

            result = pandas.concat(durations, sort=True, axis=1)
        return self.make_return(self._score.columns.get_level_values(1), result)



class TieIndexer(indexer.Indexer):
    """
    Make an index of the ties in a piece. 'start', 'continue', and 'stop' tie
    types (music21 terminology) are indexed and represented with the Humdrum
    tokens '[', '_', and ']' respectively.

    **Example:**
    from vizitka.models.indexed_piece import Importer
    ip = Importer('pathnameToScore.xml')
    ip.get('tie')
    """

    required_score_type = 'pandas.DataFrame'

    def __init__(self, score):
        """
        :param score: :class:`pandas.DataFrame` of music21 note, rest, and
            chord objects.
        :type score: :class:`pandas.DataFrame`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        """
        super(TieIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest', 'Chord')
        self._indexer_func = tie_ind_func

    # NB: This indexer inherits its run() method from indexer.py



class MeasureIndexer(indexer.Indexer): # MeasureIndexer is still experimental
    """
    Make an index of the measures in a piece. Time signatures changes do not
    cause a problem. Note that unlike most other indexers this one returns
    integer values >= 0. 0 is used for pick-up measures. For Humdrum-style
    measure representations, set the 'style' setting to 'Humdrum'.

    **Example:**
    from vizitka.models.indexed_piece import Importer
    ip = Importer('pathnameToScore.xml')
    ip.get('measure')
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = ('style')

    def __init__(self, score, part_streams, settings=None):
        """
        :param score: :class:`pandas.DataFrame` of music21 measure objects.
        :type score: :class:`pandas.DataFrame`.

        :param settings: Only setting is 'style'. If it's set to 'Humdrum',
            will return Humdrum-style measure strings.
        :type settings: Dict or None.

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        """
        super(MeasureIndexer, self).__init__(score, settings)
        self._types = ('Measure',)
        self._indexer_func = measure_ind_func
        self._settings = settings
        self._part_streams = part_streams

    def _convert_ts(self, cell):
        """If the standard approach for getting measures didn't work (often the
        case for midi pieces) then use this to transform each cell in the time
        signature indexer results to the amount of time between measures in the
        the piece."""
        if isinstance(cell, str) and len(cell) > 1:
            numerator, denominator = cell[2:].split('/')
            return int(numerator)*4/int(denominator) # the duration of this type of measure
        else:
            return nan

    def _hummify(self, cell):
        """Needed for processing of midi files."""
        if isinstance(cell, float):
            return cell
        return '=' + str(cell)

    def run(self):
        res = self._score[0].applymap(self._indexer_func)
        # The following assumes there is no anacrusis, which is the best we
        # can do if the user is parsing a midi file.
        if res.empty:
            ts = self._score[1] # time_signature indexer results
            ts = ts.applymap(self._convert_ts)
            cols = []
            for i in range(ts.shape[1]):
                col = ts.iloc[:,i].dropna()
                col.at[self._part_streams[i].highestTime] = 9999999
                m_indx = []
                for jay in range(col.size-1):
                    diff = col.index[jay+1] - col.index[jay]
                    num_mea = int(diff/col.iat[jay])
                    temp = [col.index[jay] + x*col.iat[jay] for x in range(num_mea)]
                    m_indx.extend(temp)
                    # pdb.set_trace()
                cols.append(pandas.Series(range(1, len(m_indx)), index=m_indx[:-1]))
            res = pandas.concat(cols, axis=1)
        # Make the measure tokens conform to Humdrum syntax if requested
        if (isinstance(self._settings, dict) and 'style' in self._settings
            and self._settings['style'] == 'Humdrum'):
            res = res.applymap(self._hummify)
            # Make the first measure in each part invisible. This could be a
            # measure 1 or a measure 0 if there is a pick-up.
            res.iloc[0, :] = res.iloc[0, :].apply(lambda x: str(x + '-'))

        return res



class TimeSignatureIndexer(indexer.Indexer):
    """
    Make an index of the time signatures in a piece.

    **Example:**
    from vizitka.models.indexed_piece import Importer
    ip = Importer('pathnameToScore.xml')
    ip.get('ts')
    """

    required_score_type = 'pandas.Series' # actually a list of series

    def __init__(self, score):
        """
        :param score: :class:`pandas.DataFrame` of music21 measure objects.
        :type score: :class:`pandas.DataFrame`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        """
        super(TimeSignatureIndexer, self).__init__(score, None)
        self._types = ('TimeSignature',)
        self._indexer_func = time_signature_ind_func

    def run(self):
        """
        Make a new index of the time signatures in the piece. It's no problem
        if the parts change time signatures at different times.

        :returns: The Humdrum-formated time signatures in a piece.
        :rtype: :class:`pandas.DataFrame`, or None if there are no parts.
        """
        if len(self._score) == 0: # if there are no parts
            return None
        post = [part.apply(self._indexer_func).dropna() for part in self._score]
        ret = pandas.concat(post, axis=1).dropna(how='all')
        return ret.fillna('*')



class MensurationIndexer(indexer.Indexer):
    """
    Make an index of the mensuration signs in a piece. This is independent of
    time signature changes. music21 doesn't seem to support mensuration signs,
    so development on this indexer is stalled for the moment.

    **Example:**
    from vizitka.models.indexed_piece import Importer
    ip = Importer('pathnameToScore.xml')
    ip.get('mensuration')
    """

    required_score_type = 'pandas.DataFrame'

    def __init__(self, score):
        """
        :param score: :class:`pandas.DataFrame` of music21 measure objects.
        :type score: :class:`pandas.DataFrame`

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        """
        super(MensurationIndexer, self).__init__(score, None)
        self._types = ('Mensuration',)
        self._indexer_func = mensuration_ind_func

    # NB: This indexer inherits its run() method from indexer.py
