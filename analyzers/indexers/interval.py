#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/interval.py
# Purpose:                Index vertical intervals.
#
# Copyright (C) 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
Index vertical intervals.
"""

import pandas
from music21 import note, interval, pitch
from vis.analyzers import indexer


def real_indexer(ecks, simple, qual):
    """
    Turn a notes-and-rests simultaneity into the name of the interval it represents. Note that,
    because of the u'Rest' strings, you can compare the duration of the piece in which the two
    parts do or do not have notes sounding together.

    Parameters
    ==========
    :param ecks : [music21.base.ElementWrapper]
        A two-item iterable of ElementWrapper objects, for which the "obj" attribute should be
        strings like 'Rest' or 'G4'; the upper voice should have index 0.

    :param simple : boolean
        True if intervals should be reduced to their single-octave version.

    :param qual : boolean
        True if the interval's quality should be prepended.

    Returns
    =======
    string :
        Like 'M3' or similar.
    u'Rest' :
        If one of the elements of "ecks" == u'Rest'.
    None :
        If there "ecks" has greater or fewer than two elements.
    """

    if 2 != len(ecks):
        return None
    else:
        try:
            interv = interval.Interval(note.Note(ecks[1]), note.Note(ecks[0]))
        except pitch.PitchException:
            return u'Rest'
        post = u'-' if interv.direction < 0 else u''
        if qual:
            # We must get all of the quality, and none of the size (important for AA, dd, etc.)
            q_str = u''
            for each in interv.name:
                if each in [u'A', u'M', u'P', u'm', u'd']:
                    q_str += each
            post += q_str
        if simple:
            post += u'8' if 8 == interv.generic.undirected \
                    else unicode(interv.generic.simpleUndirected)
        else:
            post += unicode(interv.generic.undirected)
        return post


# We give these functions to the multiprocessor; they're pickle-able, they let us choose settings,
# and the function still only requires one argument at run-time from the Indexer.mp_indexer().
def indexer_qual_simple(ecks):
    "Call real_indexer() with settings to print simple intervals with quality."
    return real_indexer(ecks, True, True)


def indexer_qual_comp(ecks):
    "Call real_indexer() with settings to print compound intervals with quality."
    return real_indexer(ecks, False, True)


def indexer_nq_simple(ecks):
    "Call real_indexer() with settings to print simple intervals without quality."
    return real_indexer(ecks, True, False)


def indexer_nq_comp(ecks):
    "Call real_indexer() with settings to print compound intervals without quality."
    return real_indexer(ecks, False, False)


class IntervalIndexer(indexer.Indexer):
    """
    Create an index of music21.interval.Interval objects found in the result of a NoteRestIndexer.

    This indexer does not require a score.
    """

    required_indices = [u'NoteRestIndexer']
    required_score_type = pandas.Series
    possible_settings = [u'simple or compound', u'quality']
    default_settings = {u'simple or compound': u'compound', u'quality': False}

    def __init__(self, score, settings=None, mpc=None):
        """
        Create a new IntervalIndexer. For the output format, see the docs for
        IntervalIndexer.indexer_func().

        Parameters
        ==========
        :param score : vis.models.IndexedPiece
            The piece with parts to index.

        :param settings : dict
            A dict of relevant settings, both optional. These are:
            - 'simple or compound' : 'simple' or 'compound'
                Whether intervals should be represented in their single-octave form. Defaults to
                'compound'.
            - 'quality' : boolean
                Whether to consider the quality of intervals. Optional. Defaults to False.

        :param mpc : MPController
            An optional instance of MPController. If this is present, the Indexer will use it to
            submit jobs for multiprocessing. If not present, jobs will be executed in series.

        Raises
        ======
        Nothing. There are no required settings.
        """

        if settings is None:
            settings = {}

        # Check all required settings are present in the "settings" argument
        self._settings = {}
        if 'simple or compound' in settings:
            self._settings['simple or compound'] = settings['simple or compound']
        else:
            self._settings['simple or compound'] = IntervalIndexer.default_settings['simple or compound']  # pylint: disable=C0301
        if 'quality' in settings:
            self._settings['quality'] = settings['quality']
        else:
            self._settings['quality'] = IntervalIndexer.default_settings['quality']

        super(IntervalIndexer, self).__init__(score, None, mpc)

        # Which indexer function to set?
        if self._settings['quality']:
            if 'simple' == self._settings['simple or compound']:
                self._indexer_func = indexer_qual_simple
            else:
                self._indexer_func = indexer_qual_comp
        else:
            if 'simple' == self._settings['simple or compound']:
                self._indexer_func = indexer_nq_simple
            else:
                self._indexer_func = indexer_nq_comp

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        {pandas.Series} :
            A dict of the new indices. The index of each Series corresponds to the indices of the
            Part combinations used to generate it, in the order specified to the constructor. Each
            element in the Series is an instance of music21.base.ElementWrapper.
            Example, if you stored output of run() in the "result" variable:
                result['[0, 1]'] : the highest and second highest parts
        """

        combinations = []

        # To calculate all 2-part combinations:
        for left in xrange(len(self._score)):
            # noinspection PyArgumentList
            for right in xrange(left + 1, len(self._score)):
                combinations.append([left, right])

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)

        # Do applicable post-processing, like adding a label for voice combinations.
        post = {}
        for i, combo in enumerate(combinations):
            post[str(combo)] = results[i]

        # Return the results.
        return post
