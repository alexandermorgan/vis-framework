#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/dissonance.py
# Purpose:                Indexers related to dissonance.
#
# Copyright (C) 2013, 2014 Christopher Antila, Alexander Morgan
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

Indexers related to dissonance:

* :class:`DissonanceIndexer` removes non-dissonant intervals.
* :class:`SuspensionIndexer` distinguishes suspensions from other dissonances.

**Forward Fill the IntervalIndexer**

The :class:`DissonanceIndexer` and :class:`SuspensionIndexer` require you to "forward fill" the
:class:`IntervalIndexer`. You may do this in a variety of ways, including this, where ``input_df``
is the DataFrame you wish to modify::

    input_df = input_df.T
    new_intervals = input_df.loc['interval.IntervalIndexer'].fillna(method='ffill', axis=1)
    new_multiindex = [('interval.IntervalIndexer', x) for x in list(new_intervals.index)]
    new_intervals.index = pandas.MultiIndex.from_tuples(new_multiindex)
    input_df.update(new_intervals)
    input_df = input_df.T
"""

# disable "string statement has no effect" warning---they do have an effect with Sphinx!
# pylint: disable=W0105

from numpy import nan, isnan  # pylint: disable=no-name-in-module
import pandas
from vis.analyzers import indexer
from .interval import interval_to_int

_CONS_MAKER_NODISS_LABEL = nan
_CAMB_LABEL = 'NC'
_CAMB_OTHER_LABEL = 'o'
_CAMB_NODISS_LABEL = nan

# Used by susp_ind_func() as the labels for suspensions and other dissonances. They're module-level
# so they can be changed, and possibly withstand multiprocessing... and so the unit tests can
# modify them to more easily check the classification.
_SUSP_SUSP_LABEL = 'SUSP'  # for suspensions (where the voice number is prefixed)
_SUSP_FAKE_LABEL = 'FSUS'  # for 'fake' suspensions
_SUSP_OTHER_LABEL = 'o'  # ReconciliationIndexer requires this is a string
_SUSP_NODISS_LABEL = nan


# Used by neighbour_ind_func() as the labels for neighbour notes and other dissonances. They're
# module-level so they can be changed, and possibly withstand multiprocessing... and so the unit
# tests can modify them to more easily check the classification.
_NEIGH_UN_LABEL = 'UN'  # for upper neighbour notes
_NEIGH_LN_LABEL = 'LN'  # for lower neighbour notes
_NEIGH_OTHER_LABEL = 'o'  # ReconciliationIndexer requires this is a string
_NEIGH_NODISS_LABEL = nan


# Used by passing_ind_func() as the labels for neighbour notes and other dissonances. They're
# module-level so they can be changed, and possibly withstand multiprocessing... and so the unit
# tests can modify them to more easily check the classification.
_PASS_RP_LABEL = 'RP'  # for rising passing notes (where the voice number is prefixed)
_PASS_DP_LABEL = 'DP'  # for descending passing notes (where the voice number is prefixed)
_PASS_OTHER_LABEL = 'o'  # ReconciliationIndexer requires this is a string
_PASS_NODISS_LABEL = nan

def consCheck(flagInts, crossedFlags, potens, position, low_vc):
    """
    flagInts should be a string or a list of strings of intervals that could cause a fourth or a fifth
    to be considered a consonance. crossedFlags is like flagInts but corresponds to when the consonance
    maker is in an upper voice that is crossed below the lower voice of the fourth or fifth. potens
    is a group of intervals to look for the flag interals in. The position should be either row_one,
    row_two, or row_three depending on where the potens is taken from. low_vc is the lower_voice of
    the fourth or fifth in question.
    """
    for x in potens:
        if position[x] in flagInts and x.split(',')[0] == low_vc:
            return True
        # consonance maker could be in an upper voice if there is a voice crossing.
        elif (position[x] in crossedFlags and x.split(',')[1] == low_vc):
            return True
    return False


def cons_maker_ind_func(obj):
    """
    Determines which fourths (perfect and augments) and which diminished fifths should be classified
    as consonances.
    """
    # for better legibility (i.e., shorter lines)
    diss_ind = u'dissonance.DissonanceIndexer'
    horiz_int_ind = u'interval.HorizontalIntervalIndexer'
    int_ind = u'interval.IntervalIndexer'
    cons_makers = DissonanceIndexer._CONSONANCE_MAKERS
    crs_makers = DissonanceIndexer._CROSSED_CONSONANCE_MAKERS

    row_one, row_two, row_three = obj
    # this avoids the list's reallocation penalty if we used append()
    post = [nan for _ in xrange(len(row_one[diss_ind].index))]
    for post_i, combo in enumerate(row_one[diss_ind].index):
        lower_i = int(combo.split(u',')[1])
        upper_i = int(combo.split(u',')[0])
        # is there a dissonance?
        if (isinstance(row_two[diss_ind][combo], basestring) or
            (not isnan(row_two[diss_ind][combo]))):
            # pylint: disable=invalid-name
            # set a (melodic of upper part into diss)
            a = interval_to_int(row_two[horiz_int_ind][upper_i])  # TODO: untested
            # set b (upper part melodic out of diss)
            b = interval_to_int(row_three[horiz_int_ind][upper_i])  # TODO: untested
            # set x (melodic of lower part into diss)
            x = interval_to_int(row_two[horiz_int_ind][lower_i])  # TODO: untested
            # set y (lower part melodic out of diss)
            y = interval_to_int(row_three[horiz_int_ind][lower_i])  # TODO: untested
            # set p (vert int preceding the fourth or fifth in question in the same voice pair)
            p = interval_to_int(row_one[int_ind][combo])
            # set d (the dissonant vertical interval)
            d = interval_to_int(row_two[diss_ind][combo])
            # set f (vert int following the fourth or fifth in question in the same voice pair)
            f = interval_to_int(row_three[int_ind][combo])
            post = []
            for pair in row_two[diss_ind].index:
                # a list of voice pairs to check for consonance makers in the offset of d
                check_d = row_two[int_ind].index
                # a list of voice pairs to check for consonance makers in the offset of p
                check_p = row_one[int_ind].index
                # a list of voice pairs to check for consonance makers in the offset of f
                check_f = row_three[int_ind].index
                if row_two[diss_ind][pair] in ['P4', '-P4']:
                    if 'P4' == row_two[diss_ind][pair]:
                        lower_voice = pair.split(u',')[1]
                    else: # if the voices are crossed, for this module the "upper" voice will be considered the lower voice
                        lower_voice = pair.split(u',')[0]

                    found_one = consCheck(cons_makers, crs_makers, check_d, row_two[int_ind], lower_voice)
                    # if there was no consonance maker in d's offset, look in p's if p is the same fourth as d
                    if found_one == False and p == d and a == 1 and x == 1:
                        found_one = consCheck(cons_makers, crs_makers, check_p, row_one[int_ind], lower_voice)
                    # if there was no consonance maker in d or p's offsets, look in f's if f is the same fourth as d
                    if found_one == False and f == d and b == 1 and y == 1:
                        found_one = consCheck(cons_makers, crs_makers, check_f, row_three[int_ind], lower_voice)

                    if found_one:
                        post.append(nan)
                    else:
                        post.append(row_two[diss_ind][pair])

                elif row_two[diss_ind][pair] in ['d5', '-d5']:
                    if 'd5' == row_two[diss_ind][pair]:
                        lower_voice = pair.split(u',')[1]
                    else: # if the voices are crossed, for this module the "upper" voice will be considered the lower voice
                        lower_voice = pair.split(u',')[0]

                    found_one = consCheck('M6', '-M6', check_d, row_two[int_ind], lower_voice)
                    # if there was no consonance maker in d's offset, look in p's if p is the same dim5 as d
                    if found_one == False and p == d and a == 1 and x == 1:
                        found_one = consCheck('M6', '-M6', check_p, row_one[int_ind], lower_voice)
                    # if there was no consonance maker in d or p's offsets, look in f's if f is the same dim5 as d
                    if found_one == False and f == d and b == 1 and y == 1:
                        found_one = consCheck('M6', '-M6', check_f, row_three[int_ind], lower_voice)

                    if found_one:
                        post.append(nan)
                    else:
                        post.append(row_two[diss_ind][pair])

                elif row_two[diss_ind][pair] in ['A4', '-A4']:
                    if 'A4' == row_two[diss_ind][pair]:
                        lower_voice = pair.split(u',')[1]
                    else: # if the voices are crossed, for this module the "upper" voice will be considered the lower voice
                        lower_voice = pair.split(u',')[0]

                    found_one = consCheck('m3', '-m3', check_d, row_two[int_ind], lower_voice)
                    # if there was no consonance maker in d's offset, look in p's if p is the same aug4 as d
                    if found_one == False and p == d and a == 1 and x == 1:
                        found_one = consCheck('m3', '-m3', check_p, row_one[int_ind], lower_voice)
                    # if there was no consonance maker in d or p's offsets, look in f's if f is the same dim5 as d
                    if found_one == False and f == d and b == 1 and y == 1:
                        found_one = consCheck('m3', '-m3', check_f, row_three[int_ind], lower_voice)

                    if found_one:
                        post.append(nan)
                    else:
                        post.append(row_two[diss_ind][pair])

                else:
                    post.append(row_two[diss_ind].loc[pair])
    return pandas.Series(post, index=row_two[diss_ind].index)


def susp_ind_func(obj):
    """
    Indexer function for the :class:`SuspensionIndexer`. This function processes all parts, and
    returns a :class:`Series` that should be used as a row for the :class:`DataFrame` that will be
    the resulting index returned by :class:`SuspensionIndexer`.

    The suspect dissonances occur in the second row.

    :param obj: A 3-element iterable with adjacent rows from the indexer's requested
        :class:`DataFrame`. If the first row has index ``i`` in the :class:`DataFrame`, the second
        row should have index ``i + 1``, and the third ``i + 2``.
    :type obj: 3-tuple of :class:`pandas.Series`

    :returns: A row for the new index's :class:`DataFrame`. The row's proper offset is that of the
        *second* :class:`Series` in the ``obj`` argument.
    :rtype: :class:`pandas.Series` of unicode string
    """
    # Description of the variables:
    # - a: melodic interval of upper part into suspension
    # - b: melodic interval of upper part out of suspension
    # - x: melodic interval of lower part into suspension
    # - d: dissonant harmonic interval
    # - y: melodic interval of lower part out of suspension (upper part is -2)
    # - z: d-y if y >= 1 else d-y-2 (it's the resolution vert-int)

    # for better legibility (i.e., shorter lines)
    diss_ind = u'dissonance.ConsMakerIndexer'
    horiz_int_ind = u'interval.HorizontalIntervalIndexer'
    int_ind = u'interval.IntervalIndexer'
    beat_ind = 'metre.NoteBeatStrengthIndexer'

    row_one, row_two, row_three = obj

    # this avoids the list's reallocation penalty if we used append()
    post = [nan for _ in xrange(len(row_one[diss_ind].index))]
    for post_i, combo in enumerate(row_one[diss_ind].index):
        lower_i = int(combo.split(u',')[1])
        upper_i = int(combo.split(u',')[0])
        # is there a dissonance?
        if (isinstance(row_two[diss_ind][combo], basestring) or
            (not isnan(row_two[diss_ind][combo]))):
            # pylint: disable=invalid-name
            # set a (melodic of upper part into diss)
            a = interval_to_int(row_two[horiz_int_ind][upper_i])  # TODO: untested (using end-of-interval offsets is what's untested)
            # set b (melodic of upper part out of diss)
            b = interval_to_int(row_three[horiz_int_ind][upper_i])  # TODO: untested
            # set x (melodic of lower part into diss)
            x = interval_to_int(row_two[horiz_int_ind][lower_i])  # TODO: untested
            # set d (the dissonant vertical interval)
            d = interval_to_int(row_two[diss_ind][combo])
            # set y (lower part melodic out of diss)
            y = interval_to_int(row_three[horiz_int_ind][lower_i])  # TODO: untested
            # set z (vert int after diss)
            z = interval_to_int(row_three[int_ind][combo])  # TODO: ditch z in definition of suspension
            # find the beatStrength of the dissonance and resolution
            beat_strength_one = row_one[beat_ind][lower_i] if isnan(row_one[beat_ind][upper_i]) else row_one[beat_ind][upper_i]
            beat_strength_two = row_two[beat_ind][lower_i] if isnan(row_two[beat_ind][upper_i]) else row_two[beat_ind][upper_i]  # TODO: untested
            beat_strength_three = row_three[beat_ind][lower_i] if isnan(row_three[beat_ind][upper_i]) else row_three[beat_ind][upper_i]  # TODO: untested
            # ensure there aren't any rests  # TODO: untested
            #print('a: %s, b: %s, x: %s, d: %s, y: %s, z: %s' % (a, b, x, d, y, z))  # DEBUG
            #print('beat_strength_two: %s; beat_strength_three: %s' % (beat_strength_two, beat_strength_three))  # DEBUG
            if 'Rest' in (b, d, y, z):  # TODO: untested # NB: a and x are absent because the agent needn't be present in the preparation
                post[post_i] = _SUSP_NODISS_LABEL  # TODO: untested
            # deal with z
            elif (1 == x and ((b >= 1 and d + b == z) or  # if the upper voice ascends out of d
                              (d + b + 2 == z))  # if the upper voice descends out of d
                  and beat_strength_two > beat_strength_three):  # strong-beat diss  # TODO: untested
                post[post_i] = ''.join((str(lower_i), ':', _SUSP_SUSP_LABEL))
           # for fake suspensions; z can == 3 because if the two fourths are one note, a new event may not be generated
            elif ((2 == a or -2 == a) and (1 == x or 8 == x or -8 == x) and 4 == d and
                  (1 == y or 8 == y or -8 == y) and
                  ((1 == b and 4 == z and beat_strength_one > beat_strength_two and beat_strength_three > beat_strength_two) or
                   (-2 == b and 3 == z and beat_strength_one > beat_strength_two and beat_strength_three == beat_strength_two))):
                post[post_i] = ''.join((str(upper_i), ':', _SUSP_FAKE_LABEL))
            elif (1 == a and ((y >= 1 and (d - y == z or (d == 2 and z == 8))) or  # if the lower voice ascends out of d, the last bit is for 9-8 suspensions.
                              (d - y - 2 == z) or   # if the lower voice descends out of d
                              ((y == 8 or y == -8) and d -1 == z)) # TODO: verify this logic, meant to apply to octave leaps in bass at moment of resolution.
                  and beat_strength_two > beat_strength_three):  # strong-beat diss  # TODO: untested
                post[post_i] = ''.join((str(upper_i), ':', _SUSP_SUSP_LABEL))
            else:
                post[post_i] = _SUSP_OTHER_LABEL
        else:
            post[post_i] = _SUSP_NODISS_LABEL
    return pandas.Series(post, index=row_one[diss_ind].index)


def neighbour_ind_func(obj):
    # TODO: NOTE: TEST: this whole indexer is untested
    """
    Indexer function for the :class:`NeighbourNoteIndexer`. This function processes all parts, and
    returns a :class:`Series` that should be used as a row for the :class:`DataFrame` that will be
    the resulting index returned by :class:`NeighbourNoteIndexer`.

    The suspect dissonances occur in the second row.

    :param obj: A 3-element iterable with adjacent rows from the indexer's requested
        :class:`DataFrame`. If the first row has index ``i`` in the :class:`DataFrame`, the second
        row should have index ``i + 1``, and the third ``i + 2``.
    :type obj: 3-tuple of :class:`pandas.Series`

    :returns: A row for the new index's :class:`DataFrame`. The row's proper offset is that of the
        *second* :class:`Series` in the ``obj`` argument.
    :rtype: :class:`pandas.Series` of unicode string
    """
    # Description of the variables:
    # - a: melodic interval of upper part into dissonance
    # - b: melodic interval of upper part out of dissonance
    # - x: melodic interval of lower part into dissonance
    # - y: melodic interval of lower part out of dissonance

    # TODO: incorporate these metric things
    # -it is on a weak half and its duration is one half note or less,  OR
    # -it is on a weak quarter and its duration is one quarter or less,  OR
    # -it is on a weak eighth and its duration is one eighth or less.

    #Subcategories of the above: N1u and N1l (upper and lower neighbours).

    # for better legibility (i.e., shorter lines)
    diss_ind = u'dissonance.ConsMakerIndexer'
    horiz_int_ind = u'interval.HorizontalIntervalIndexer'
    int_ind = u'interval.IntervalIndexer'
    beat_ind = 'metre.NoteBeatStrengthIndexer'
    cons_ints = [8, 6, 5, 3, 1, -3, -5, -6, -8]

    row_one, row_two, row_three = obj

    # this avoids the list's reallocation penalty if we used append()
    post = [nan for _ in xrange(len(row_one[diss_ind].index))]
    for post_i, combo in enumerate(row_one[diss_ind].index):
        lower_i = int(combo.split(u',')[1])
        upper_i = int(combo.split(u',')[0])
        # is there a dissonance?
        if (isinstance(row_two[diss_ind][combo], basestring) or
            (not isnan(row_two[diss_ind][combo]))):
            # pylint: disable=invalid-name
            # set a (melodic of upper part into diss)
            a = interval_to_int(row_two[horiz_int_ind][upper_i])
            # set b (melodic of upper part out of diss)
            b = interval_to_int(row_three[horiz_int_ind][upper_i])
            # set c (harmonic interval preceding the dissonance)
            c = interval_to_int(row_one[int_ind][combo])
            # set d (the dissonant vertical interval)
            d = interval_to_int(row_two[diss_ind][combo])
            # set x (melodic of lower part into diss)
            x = interval_to_int(row_two[horiz_int_ind][lower_i])
            # set y (lower part melodic out of diss)
            y = interval_to_int(row_three[horiz_int_ind][lower_i])
            # set z (vert int after diss)
            z = interval_to_int(row_three[int_ind][combo])
            # find the beatStrength of the dissonance and resolution
            beat_strength_one = row_one[beat_ind][lower_i] if isnan(row_one[beat_ind][upper_i]) else row_one[beat_ind][upper_i]
            beat_strength_two = row_two[beat_ind][lower_i] if isnan(row_two[beat_ind][upper_i]) else row_two[beat_ind][upper_i]
            beat_strength_three = row_three[beat_ind][lower_i] if isnan(row_three[beat_ind][upper_i]) else row_three[beat_ind][upper_i]
            # ensure there aren't any rests
            #print('a: %s, b: %s, x: %s, y: %s' % (a, b, x, y))  # DEBUG
            #print('beat_strength_two: %s; beat_strength_three: %s' % (beat_strength_two, beat_strength_three))  # DEBUG
            if 'Rest' in (a, x):
                post[post_i] = _NEIGH_NODISS_LABEL
            # filter out what would be accented neighbour tones
            elif (beat_strength_one < beat_strength_two) or (beat_strength_three < beat_strength_two):
                post[post_i] = _NEIGH_NODISS_LABEL
            # see if it's an upper neighbour in the upper part
            elif a == 2 and x == 1 and b == -2 and c in cons_ints:
                post[post_i] = ''.join((str(upper_i), ':', _NEIGH_UN_LABEL))

            # see if it's a lower neighbour in the upper part
            elif a == -2 and x == 1 and b == 2 and c in cons_ints:
                post[post_i] = ''.join((str(upper_i), ':', _NEIGH_LN_LABEL))

            # see if it's an upper neighbour in the lower part
            elif x == 2 and a == 1 and y == -2 and c in cons_ints:
                post[post_i] = ''.join((str(lower_i), ':', _NEIGH_UN_LABEL))

            # see if it's a lower neighbour in the lower part
            elif x == -2 and a == 1 and y == 2 and c in cons_ints:
                post[post_i] = ''.join((str(lower_i), ':', _NEIGH_LN_LABEL))
            else:
                post[post_i] = _NEIGH_OTHER_LABEL
        else:
            post[post_i] = _NEIGH_NODISS_LABEL
    return pandas.Series(post, index=row_one[diss_ind].index)


def passing_ind_func(obj):
    # TODO: NOTE: TEST: this whole indexer is untested
    """
    Indexer function for the :class:`PassingNoteIndexer`. This function processes all parts, and
    returns a :class:`Series` that should be used as a row for the :class:`DataFrame` that will be
    the resulting index returned by :class:`PassingNoteIndexer`.

    The suspect dissonances occur in the second row.

    :param obj: A 3-element iterable with adjacent rows from the indexer's requested
        :class:`DataFrame`. If the first row has index ``i`` in the :class:`DataFrame`, the second
        row should have index ``i + 1``, and the third ``i + 2``.
    :type obj: 3-tuple of :class:`pandas.Series`

    :returns: A row for the new index's :class:`DataFrame`. The row's proper offset is that of the
        *second* :class:`Series` in the ``obj`` argument.
    :rtype: :class:`pandas.Series` of unicode string
    """
    # for better legibility (i.e., shorter lines)
    diss_ind = u'dissonance.ConsMakerIndexer'
    horiz_int_ind = u'interval.HorizontalIntervalIndexer'
    int_ind = u'interval.IntervalIndexer'
    cons_ints = [8, 6, 5, 3, 1, -3, -5, -6, -8]
    row_one, row_two, row_three = obj

    # this avoids the list's reallocation penalty if we used append()
    post = [_PASS_NODISS_LABEL for _ in xrange(len(row_one[diss_ind].index))]
    for post_i, combo in enumerate(row_one[diss_ind].index):
        lower_i = int(combo.split(u',')[1])
        upper_i = int(combo.split(u',')[0])
        # is there a dissonance?
        if (isinstance(row_two[diss_ind][combo], basestring) or
            (not isnan(row_two[diss_ind][combo]))):
            # pylint: disable=invalid-name
            # set a (melodic of upper part into diss)
            a = interval_to_int(row_two[horiz_int_ind][upper_i])
            # set b (melodic of upper part out of diss)
            b = interval_to_int(row_three[horiz_int_ind][upper_i])
            # set p (harmonic interval preceding the dissonance)
            p = interval_to_int(row_one[int_ind][combo])
            # set d (the dissonant vertical interval)
            d = interval_to_int(row_two[diss_ind][combo])
            # set r (vert int after diss)
            r = interval_to_int(row_three[int_ind][combo])
            # set x (melodic of lower part into diss)
            x = interval_to_int(row_two[horiz_int_ind][lower_i])
            # set y (lower part melodic out of diss)
            y = interval_to_int(row_three[horiz_int_ind][lower_i])

            if 'Rest' in (a, p, x):
                post[post_i] = _PASS_OTHER_LABEL

            elif a == -2 and x == 1 and b == -2 and p in cons_ints: # upper voice is descending
                post[post_i] = ''.join((str(upper_i), ':', _PASS_DP_LABEL))

            elif a == 2 and x == 1 and b == 2 and p in cons_ints: # upper voice is rising
                post[post_i] = ''.join((str(upper_i), ':', _PASS_RP_LABEL))

            elif x == -2 and a == 1 and y == -2 and p in cons_ints: # lower voice descending
                post[post_i] = ''.join((str(lower_i), ':', _PASS_DP_LABEL))

            elif x == 2 and a == 1 and y == 2 and p in cons_ints: # lower voice rising
                post[post_i] = ''.join((str(lower_i), ':', _PASS_RP_LABEL))

            else:
                post[post_i] = _PASS_OTHER_LABEL
        else:
            post[post_i] = _PASS_NODISS_LABEL
    return pandas.Series(post, index=row_one[diss_ind].index)

def cambiata_ind_func(obj):
    """
    Doc string.
    """
    # for better legibility (i.e., shorter lines)
    diss_ind = u'dissonance.ConsMakerIndexer'
    horiz_int_ind = u'interval.HorizontalIntervalIndexer'
    int_ind = u'interval.IntervalIndexer'
    beat_ind = 'metre.NoteBeatStrengthIndexer'
    row_one, row_two, row_three, row_four = obj

    # this avoids the list's reallocation penalty if we used append()
    post = [_PASS_NODISS_LABEL for _ in xrange(len(row_one[diss_ind].index))]
    for post_i, combo in enumerate(row_one[diss_ind].index):
        lower_i = int(combo.split(u',')[1])
        upper_i = int(combo.split(u',')[0])
        # is there a dissonance?
        if (isinstance(row_two[diss_ind][combo], basestring) or
            (not isnan(row_two[diss_ind][combo]))):
            # pylint: disable=invalid-name
            # set a (melodic of upper part into diss)
            a = interval_to_int(row_two[horiz_int_ind][upper_i])
            # set b (melodic of upper part out of diss)
            b = interval_to_int(row_three[horiz_int_ind][upper_i])
            # set c (melodic of upper part from third to fourth event)
            c = interval_to_int(row_four[horiz_int_ind][upper_i])
            # set p (harmonic interval preceding the dissonance)
            p = interval_to_int(row_one[int_ind][combo])
            # set d (the dissonant vertical interval)
            d = interval_to_int(row_two[diss_ind][combo])
            # set x (melodic of lower part into diss)
            x = interval_to_int(row_two[horiz_int_ind][lower_i])
            # set y (lower part melodic out of diss)
            y = interval_to_int(row_three[horiz_int_ind][lower_i])
            # set z (lower part melodic from third to fourth event)
            z = interval_to_int(row_four[horiz_int_ind][lower_i])
            # beat strength of dissonance (should be less than .5)
            beat_strength_two = row_two[beat_ind][lower_i] if isnan(row_two[beat_ind][upper_i]) else row_two[beat_ind][upper_i]


            if a == -2 and x == 1 and b == -3 and y == 1 and c == 2 and beat_strength_two < .5:
                post[post_i] = ''.join((str(upper_i), ':', _CAMB_LABEL))
            elif x == -2 and a == 1 and y == -3 and b ==1 and z == 2 and beat_strength_two < .5:
                post[post_i] = ''.join((str(lower_i), ':', _CAMB_LABEL))
            else:
                post[post_i] = _CAMB_OTHER_LABEL
        else:
            post[post_i] = _CAMB_NODISS_LABEL
    return pandas.Series(post, index=row_one[diss_ind].index)


def reconciliation_func(obj):
    '''
    Indexer function for the :class:`ReconciliationIndexer`.

    :param obj: A row from the :class:`DataFrame` of indices given to :class:`ReconciliationIndexer`.
    :type obj: :class:`pandas.Series`

    :returns: Reconciled results for this offset.
    :rtype: :class:`pandas.Series`

    .. note:: The length of the returned :class:`Series` is the same as the number of parts in the
        original score. This is usually different than the length of the input :class:`Series`
        because the number of part combinations is almost never equal to the number of parts (only
        for scores with three parts is this true).
    '''
    susp_ind = 'dissonance.SuspensionIndexer'
    neigh_ind = 'dissonance.NeighbourNoteIndexer'
    pass_ind = 'dissonance.PassingNoteIndexer'
    camb_ind = 'dissonance.NotaCambiataIndexer'

    # make "post" dict with one entry for each of the parts
    input_parts = []
    for combo in obj[susp_ind].index:
        input_parts.append(combo.split(',')[0])
        input_parts.append(combo.split(',')[1])
    input_parts = set(input_parts)
    post = {x: None for x in input_parts}

    for combo_i in obj[susp_ind].index:
        # for each combination
        combowise = []
        for ind in (susp_ind, neigh_ind, pass_ind, camb_ind):
            # compile dissonances specific to this combination
            g = (str(obj[ind][combo_i]))
            if g != 'nan':
                print g
            if (not isinstance(obj[ind][combo_i], basestring)) and isnan(obj[ind][combo_i]):
                continue
            else:
                combowise.append(obj[ind][combo_i])

        if 0 == len(combowise):
            continue

        # if we only have "other" categorizations, then we'll just use that
        for signature in combowise:
            if signature not in (_SUSP_OTHER_LABEL, _NEIGH_OTHER_LABEL, _PASS_OTHER_LABEL, _CAMB_OTHER_LABEL):
                print('break (combowise is %s)' % combowise)  # DEBUG
                break
        else:
            print('else  (combowise is %s)' % combowise)  # DEBUG
            post[combo_i.split(',')[0]] = 'o'
            post[combo_i.split(',')[1]] = 'o'

        # filter the "other" categorizations
        signatures = filter(lambda x: x not in (_SUSP_OTHER_LABEL, _NEIGH_OTHER_LABEL, _PASS_OTHER_LABEL, _CAMB_OTHER_LABEL), combowise)
        #signatures = combowise

        # add the classification
        for signature in signatures:
            # add a "good" classification to the relevant voice
            split_signature = signature.split(':')
            if (post[split_signature[0]] is None or post[split_signature[0]] in (_SUSP_OTHER_LABEL,
                                                                                _NEIGH_OTHER_LABEL,
                                                                                _PASS_OTHER_LABEL,
                                                                                _CAMB_OTHER_LABEL)):
                # if there's no existing classification, or it's "other," then overwrite it
                post[split_signature[0]] = split_signature[1]
            elif post[split_signature[0]] != split_signature[1]:
                # if there's an existing "good" classification, add to it
                post[split_signature[0]] += ',' + split_signature[1]

    return pandas.Series(post, index=input_parts)


class DissonanceIndexer(indexer.Indexer):
    """
    Remove consonant intervals. All remaining intervals are a "dissonance." Refer to the
    :const:`CONSONANCES` constant for a list of consonances. A perfect fourth is sometimes
    consonant---refer to the ``'special_P4'`` setting for more information.
    """

    CONSONANCES = [u'Rest', u'P1', u'm3', u'M3', u'P5', u'm6', u'M6', u'P8',
                   u'-m3', u'-M3', u'-P5', u'-m6', u'-M6', u'-P8']
    _CONSONANCE_MAKERS = [u'm3', u'M3', u'P5']  # TODO: this should probably include 'd5' # APM- probably not since the original P4 would then be an A4
    _CROSSED_CONSONANCE_MAKERS = [u'-m3', u'-M3', u'-P5']
    _UPPER_VOICE_CONS_MAKERS = [u'P1', u'P8'] # DEBUG - P1 is necessary because of an unrelated bug in the simple intervals. Putting in sixths caused some suspensions to be missed.
    required_score_type = 'pandas.DataFrame'
    default_settings = {'special_P4': True, 'special_d5': True}
    possible_settings = ['special_P4', 'special_d5']
    """
    :keyword bool 'special_P4': Whether to account for the Perfect Fourth's "special"
        characteristic of being a dissonance only when no major or minor third or fifth appears
        below it. If this is ``True``, an additional indexing process is run that removes all
        fourths "under" which the following intervals appear: m3, M3, P5.
    :keyword bool 'special_d5': Whether to account for the Diminished Fifth's "special"
        characteristic of being consonant when a Major Sixth appears at any point below the
        lowest note.
    """

    def __init__(self, score, settings=None):
        """
        :param score: The output from :class:`~vis.analyzers.indexers.interval.IntervalIndexer`.
            You *must* include interval quality and *must not* use compound intervals.
        :type score: :class:`pandas.DataFrame`
        :param NoneType settings: There are no settings.

        .. warning:: The :class:`DissonanceIndexer` requires the results of the
            :class:`IntervalIndexer` to have been "forward filled," or there will be errors. Do not
            "forward fill" other indices.

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        self._settings = {'special_P4': DissonanceIndexer.default_settings['special_P4'],
                          'special_d5': DissonanceIndexer.default_settings['special_d5']}
        #if settings is not None:  # TODO: test this stuff
            #if u'special_P4' in settings:
                #self._settings[u'special_P4'] = settings[u'special_P4']
            #if 'special_d5' in settings:
                #self._settings['special_d5'] = settings['special_d5']
        super(DissonanceIndexer, self).__init__(score, None)

    @staticmethod
    def nan_consonance(simul):
        """
        Used internally by the :class:`DissonanceIndexer`.

        Convert all "consonant" values to nan. The "consonant" intervals are those contained in
        :const:`DissonanceIndexer.CONSONANCES`.

        :param simul: A simultaneity with arbitrary vertical intervals.
        :type simul: :class:`pandas.Series`

        :returns: A :class:`Series` of the same length, where all "consonances" have been replaced
            with nan.
        :rtype: :class:`pandas.Series`
        """
        return simul.map(lambda x: nan if x in DissonanceIndexer.CONSONANCES else x)

    @staticmethod
    def special_fourths(simul):
        """
        Used internally by the :class:`DissonanceIndexer`.

        Replace all consonant fourths in a :class:`Series` with nan. The method checks each part
        combination and, if it finds a ``'P4'`` or a ``'-P4'``, checks all part combinations for a
        major or minor third or perfect fifth sounding below the lower pitch of the fourth.

        For example, consider the following simultaneity:

        +------------------+----------+
        | Part Combination | Interval |
        +==================+==========+
        | 0,1              | M3       |
        +------------------+----------+
        | 0,2              | P4       |
        +------------------+----------+
        | 0,3              | M3       |
        +------------------+----------+
        | 1,2              | M3       |
        +------------------+----------+
        | 1,3              | M3       |
        +------------------+----------+
        | 2,3              | P8       |
        +------------------+----------+

        On encountering ``'P4'`` in the ``'0,2'`` part combination, :meth:`_special_fourths` only
        looks at the ``'2,3'`` combination for a third or fifth. Finding an octave, this fourth
        is considered "dissonant," and therefore retained.

        For this reason, it's very important that the index has good part-combination labels that
        follow the ``'int,int'`` format, as outputted by the :class:`IntervalIndexer`.

        :param simul: A row of the :class:`DataFrame` given to :class:`DissonanceIndexer`.
        :type simul: :class:`pandas.Series`
        """
        post = []
        for combo in simul.index:
            if u'P4' == simul.loc[combo]:
                lower_voice = combo.split(u',')[1]
                investigate_these = []
                for possibility in simul.index:
                    if possibility.split(u',')[0] == lower_voice:
                        investigate_these.append(possibility)
                found_one = False
                for possibility in investigate_these:
                    if simul.loc[possibility] in DissonanceIndexer._CONSONANCE_MAKERS:
                        found_one = True
                        break
                if found_one == False: # In some cases you have to look from the top voice down too.
                    upper_voice = combo.split(u',')[0]
                    investigate_also = []
                    for possibility in simul.index:
                        if possibility.split(u',')[0] == upper_voice:
                            investigate_also.append(possibility)
                    for possibility in investigate_also:
                        if simul.loc[possibility] in DissonanceIndexer._UPPER_VOICE_CONS_MAKERS:
                            found_one = True
                            break
                if found_one:
                    post.append(nan)
                else:
                    post.append(simul.loc[combo])
            elif u'-P4' == simul.loc[combo]:
                lower_voice = combo.split(u',')[0]
                investigate_these = []
                for possibility in simul.index:
                    if possibility.split(u',')[0] == lower_voice:
                        investigate_these.append(possibility)
                found_one = False
                for possibility in investigate_these:
                    if simul.loc[possibility] in DissonanceIndexer._CONSONANCE_MAKERS:
                        found_one = True
                        break
                if found_one:
                    post.append(nan)
                else:
                    post.append(simul.loc[combo])
            else:
                post.append(simul.loc[combo])
        return pandas.Series(post, index=simul.index)

    @staticmethod
    def special_fifths(simul):
        """
        Used internally by the :class:`DissonanceIndexer`.

        Replace all consonant fifths in a :class:`Series` with nan. The method checks each part
        combination and, if it finds a ``'d5'``, checks all part combinations for a major sixth
        sounding below the lower note of the fifth.

        For example, consider the following simultaneity:

        +------------------+----------+
        | Part Combination | Interval |
        +==================+==========+
        | 0,1              | M3       |
        +------------------+----------+
        | 0,2              | d5       |
        +------------------+----------+
        | 0,3              | M3       |
        +------------------+----------+
        | 1,2              | M3       |
        +------------------+----------+
        | 1,3              | M3       |
        +------------------+----------+
        | 2,3              | P8       |
        +------------------+----------+

        On encountering ``'d5'`` in the ``'0,2'`` part combination, :meth:`_special_fourths` only
        looks at the ``'2,3'`` combination for a major sixth. Finding an octave, this fifth
        is considered "dissonant," and therefore retained.

        For this reason, it's very important that the index has good part-combination labels that
        follow the ``'int,int'`` format, as outputted by the :class:`IntervalIndexer`.
        """
        ## TODO: figure this out for d5s that arise from a voice crossing.
        post = []
        for combo in simul.index:
            if u'd5' == simul.loc[combo]:
                lower_voice = combo.split(u',')[1]
                investigate_these = []
                for possibility in simul.index:
                    if possibility.split(u',')[0] == lower_voice:
                        investigate_these.append(possibility)
                found_one = False
                for possibility in investigate_these:
                    if 'M6' == simul.loc[possibility]:  # in DissonanceIndexer._CONSONANCE_MAKERS:
                        found_one = True
                        break
                if found_one:
                    post.append(nan)
                else:
                    post.append(simul.loc[combo])
            else:
                post.append(simul.loc[combo])
        return pandas.Series(post, index=simul.index)

    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` of the new indices. The columns have a :class:`MultiIndex`;
            refer to the example below for more details.
        :rtype: :class:`pandas.DataFrame`

        **Example:**

        >>> the_score = music21.converter.parse('sibelius_5-i.mei')
        >>> the_score.parts[5]
        (the first clarinet Part)
        >>> the_notes = NoteRestIndexer(the_score).run()
        >>> the_notes['noterest.NoteRestIndexer']['5']
        (the first clarinet Series)
        >>> the_intervals = IntervalIndexer(the_notes).run()
        >>> the_intervals['interval.IntervalIndexer']['5,6']
        (Series with vertical intervals between first and second clarinet)
        >>> the_dissonances = DissonanceIndexer(the_notes).run()
        >>> the_intervals['dissonance.DissonanceIndexer']['5,6']
        (Series with only the dissonant intervals between first and second clarinet)
        """
        post = self._score['interval.IntervalIndexer']
        #if self._settings[u'special_P4'] is True:
            #post = post.apply(DissonanceIndexer.special_fourths, axis=1)
        if self._settings[u'special_d5'] is True:
            post = post.apply(DissonanceIndexer.special_fifths, axis=1)  # TODO: test this branch works
        post = post.apply(DissonanceIndexer.nan_consonance, axis=1)
        return self.make_return([x for x in post.columns],
                                [post[x] for x in post.columns])


class ConsMakerIndexer(indexer.Indexer):
    """
    Classify fourths (perfect and augmented) and diminished fifths as consonant or dissonant.

    Inputted results from the :mod:`interval` module require the same settings as were given to
    the :class:`DissonanceIndexer.
    """

    required_score_type = 'pandas.DataFrame'

    # Text for the RuntimeError raised when a score has fewer than 3 event offsets.
    _TOO_SHORT_ERROR = u'ConsMakerIndexer: input must have at least 3 events'

    def __init__(self, score):
        """
        :param score: The input from which to produce a new index. You must provide a
            :class:`DataFrame` with results from the
            :class:`~vis.analyzers.indexers.interval.IntervalIndexer`, the
            :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`,
            :class:`~vis.analyzers.indexers.metre.NoteBeatStrengthIndexer`, and the
            :class:`DissonanceIndexer. The :class:`DataFrame` may contain results from additional
            indexers, which will be ignored.
        :type score: :class:`pandas.DataFrame`

        .. warning:: The :class:`ConsMakerIndexer` requires the results of the
            :class:`IntervalIndexer` to have been "forward filled," or there will be errors. Do not
            "forward fill" other indices.

        .. note:: The :meth:`run` method will raise a :exc:`KeyError` if ``score`` does not contain
            results from the required indices.

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        :raises: :exc:`RuntimeError` if the ``score`` argument has fewer than three event offsets,
            which is the minimum required for a suspension (preparation, dissonance, resolution).
            An exception here prevents an error later.
        """
        super(ConsMakerIndexer, self).__init__(score)
        if len(score.index) < 3:
            raise RuntimeError(ConsMakerIndexer._TOO_SHORT_ERROR)
        self._indexer_func = cons_maker_ind_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` with suspensions labeled *and* all inputted indices.
        :rtype: :class:`pandas.DataFrame`

        :raises: :exc:`KeyError` if the ``score`` given to the constructor was an
            improperly-formatted :class:`DataFrame` (e.g., it does not contain results of the
            required indexers, or the columns do not have a :class:`MultiIndex`).
        """
        # NB: it's actually cons_maker_ind_func() that raises the KeyError

        # this avoids the list's reallocation penalty if we used append()
        post = [nan for _ in xrange(len(self._score.index))]
        for i in xrange(len(self._score.index) - 2):
            post[i + 1] = cons_maker_ind_func((self._score.iloc[i],
                                         self._score.iloc[i + 1],
                                         self._score.iloc[i + 2]))

        # This indexer should ultimately be able to handle single events but cannot yet.
        for i in [0, -1]:
            post[i] = pandas.Series([_CONS_MAKER_NODISS_LABEL for _ in xrange(len(post[1]))],
                                    index=post[1].index)

        # Convert from the list of Series into a DataFrame. Each inputted Series becomes a row.
        post = pandas.DataFrame({j: post[i] for i, j in enumerate(self._score.index)}).T

        # the part names are the column names
        post = self.make_return(list(post.columns), [post[i] for i in post.columns])
        return pandas.concat(objs=[self._score, post], axis=1, join='outer')


class SuspensionIndexer(indexer.Indexer):
    """
    Mark dissonant intervals as a suspension or another dissonance.

    Inputted results from the :mod:`interval` module require the same settings as were given to
    the :class:`DissonanceIndexer.
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = [u'suspension_label', u'other_label']
    """
    You may change the words used to label suspensions and other dissonances.

    :keyword 'suspension_label': The string used to label suspensions.
    :type 'suspension_label': basestring
    :keyword 'other_label': The string used to label other dissonances.
    :type 'other_label': basestring
    """

    default_settings = {u'suspension_label': u'susp', u'other_label': u''}

    # Text for the RuntimeError raised when a score has fewer than 3 event offsets.
    _TOO_SHORT_ERROR = u'SuspensionIndexer: input must have at least 3 events'

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index. You must provide a
            :class:`DataFrame` with results from the
            :class:`~vis.analyzers.indexers.interval.IntervalIndexer`, the
            :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`,
            :class:`~vis.analyzers.indexers.metre.NoteBeatStrengthIndexer`, and the
            :class:`DissonanceIndexer. The :class:`DataFrame` may contain results from additional
            indexers, which will be ignored.
        :type score: :class:`pandas.DataFrame`
        :param dict settings: A dict with settings as specified in
            :attr:`~SuspensionIndexer.possible_settings`.

        .. warning:: The :class:`SuspensionIndexer` requires the results of the
            :class:`IntervalIndexer` to have been "forward filled," or there will be errors. Do not
            "forward fill" other indices.

        .. note:: The :meth:`run` method will raise a :exc:`KeyError` if ``score`` does not contain
            results from the required indices.

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        :raises: :exc:`RuntimeError` if the ``score`` argument has fewer than three event offsets,
            which is the minimum required for a suspension (preparation, dissonance, resolution).
            An exception here prevents an error later.
        """
        super(SuspensionIndexer, self).__init__(score, None)
        if len(score.index) < 3:
            raise RuntimeError(SuspensionIndexer._TOO_SHORT_ERROR)
        self._indexer_func = susp_ind_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` with suspensions labeled *and* all inputted indices.
        :rtype: :class:`pandas.DataFrame`

        :raises: :exc:`KeyError` if the ``score`` given to the constructor was an
            improperly-formatted :class:`DataFrame` (e.g., it does not contain results of the
            required indexers, or the columns do not have a :class:`MultiIndex`).
        """
        # NB: it's actually susp_ind_func() that raises the KeyError

        # this avoids the list's reallocation penalty if we used append()
        post = [nan for _ in xrange(len(self._score.index))]
        for i in xrange(len(self._score.index) - 2):
            post[i + 1] = susp_ind_func((self._score.iloc[i],
                                         self._score.iloc[i + 1],
                                         self._score.iloc[i + 2]))

        # Add post for the final two offsets in the piece. They obviously can't be suspensions,
        # since they wouldn't  be prepared or resolved. (Make sure we use the same index as the
        # other rows, or we'll have empty columns in the output).
        for i in [0, -1]:
            post[i] = pandas.Series([_SUSP_NODISS_LABEL for _ in xrange(len(post[1]))],
                                    index=post[1].index)

        # Convert from the list of Series into a DataFrame. Each inputted Series becomes a row.
        post = pandas.DataFrame({j: post[i] for i, j in enumerate(self._score.index)}).T

        # the part names are the column names
        post = self.make_return(list(post.columns), [post[i] for i in post.columns])
        return pandas.concat(objs=[self._score, post], axis=1, join='outer')


class NeighbourNoteIndexer(indexer.Indexer):
    # TODO: NOTE: TEST: this whole indexer is untested
    # TODO: NOTE: TEST: this whole court is out of order!
    """
    Mark dissonant intervals as a neighbour note or another dissonance.

    Inputted results from the :mod:`interval` module require the same settings as were given to
    the :class:`DissonanceIndexer.
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = []
    default_settings = {}

    # Text for the RuntimeError raised when a score has fewer than 3 event offsets.
    _TOO_SHORT_ERROR = u'NeighbourNoteIndexer: input must have at least 3 events'

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index. You must provide a
            :class:`DataFrame` with results from the
            :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`,
            :class:`~vis.analyzers.indexers.metre.NoteBeatStrengthIndexer`, and the
            :class:`DissonanceIndexer. The :class:`DataFrame` may contain results from additional
            indexers, which will be ignored.
        :type score: :class:`pandas.DataFrame`
        :param settings: This indexer has no settings, so this is ignored.
        :type settings: NoneType

        .. warning:: The :class:`NeighbourNoteIndexer` requires the results of the
            :class:`IntervalIndexer` to have been "forward filled," or there will be errors. Do not
            "forward fill" other indices.

        .. note:: The :meth:`run` method will raise a :exc:`KeyError` if ``score`` does not contain
            results from the required indices.

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        :raises: :exc:`RuntimeError` if the ``score`` argument has fewer than three event offsets,
            which is the minimum required for a suspension (preparation, dissonance, resolution).
            An exception here prevents an error later.
        """
        super(NeighbourNoteIndexer, self).__init__(score, None)
        if len(score.index) < 3:
            raise RuntimeError(NeighbourNoteIndexer._TOO_SHORT_ERROR)
        self._indexer_func = neighbour_ind_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` with suspensions labeled *and* all inputted indices.
        :rtype: :class:`pandas.DataFrame`

        :raises: :exc:`KeyError` if the ``score`` given to the constructor was an
            improperly-formatted :class:`DataFrame` (e.g., it does not contain results of the
            required indexers, or the columns do not have a :class:`MultiIndex`).
        """
        # NB: it's actually susp_ind_func() that raises the KeyError

        # this avoids the list's reallocation penalty if we used append()
        post = [nan for _ in xrange(len(self._score.index))]
        for i in xrange(len(self._score.index) - 2):
            post[i + 1] = neighbour_ind_func((self._score.iloc[i],
                                              self._score.iloc[i + 1],
                                              self._score.iloc[i + 2]))

        # Add post for the final two offsets in the piece. They obviously can't be suspensions,
        # since they wouldn't  be prepared or resolved. (Make sure we use the same index as the
        # other rows, or we'll have empty columns in the output).
        for i in [0, -1]:
            post[i] = pandas.Series([_NEIGH_NODISS_LABEL for _ in xrange(len(post[1]))],
                                    index=post[1].index)

        # Convert from the list of Series into a DataFrame. Each inputted Series becomes a row.
        post = pandas.DataFrame({j: post[i] for i, j in enumerate(self._score.index)}).T

        # the part names are the column names
        post = self.make_return(list(post.columns), [post[i] for i in post.columns])
        return pandas.concat(objs=[self._score, post], axis=1, join='outer')


class PassingNoteIndexer(indexer.Indexer):
    # TODO: NOTE: TEST: this whole indexer is untested
    """
    Mark dissonant intervals as a passing note or another dissonance.

    Inputted results from the :mod:`interval` module require the same settings as were given to
    the :class:`DissonanceIndexer.
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = []
    default_settings = {}

    # Text for the RuntimeError raised when a score has fewer than 3 event offsets.
    _TOO_SHORT_ERROR = u'PassingNoteIndexer: input must have at least 3 events'

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index. You must provide a
            :class:`DataFrame` with results from the
            :class:`~vis.analyzers.indexers.interval.IntervalIndexer`, the
            :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`, and the
            :class:`DissonanceIndexer. The :class:`DataFrame` may contain results from additional
            indexers, which will be ignored.
        :type score: :class:`pandas.DataFrame`
        :param settings: This indexer has no settings, so this is ignored.
        :type settings: NoneType

        .. warning:: The :class:`PassingNoteIndexer` requires the results of the
            :class:`IntervalIndexer` to have been "forward filled," or there will be errors. Do not
            "forward fill" other indices.

        .. note:: The :meth:`run` method will raise a :exc:`KeyError` if ``score`` does not contain
            results from the required indices.

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        :raises: :exc:`RuntimeError` if the ``score`` argument has fewer than three event offsets,
            which is the minimum required for a suspension (preparation, dissonance, resolution).
            An exception here prevents an error later.
        """
        super(PassingNoteIndexer, self).__init__(score, None)
        if len(score.index) < 3:
            raise RuntimeError(PassingNoteIndexer._TOO_SHORT_ERROR)
        self._indexer_func = passing_ind_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` with suspensions labeled *and* all inputted indices.
        :rtype: :class:`pandas.DataFrame`

        :raises: :exc:`KeyError` if the ``score`` given to the constructor was an
            improperly-formatted :class:`DataFrame` (e.g., it does not contain results of the
            required indexers, or the columns do not have a :class:`MultiIndex`).
        """
        # NB: it's actually susp_ind_func() that raises the KeyError

        # this avoids the list's reallocation penalty if we used append()
        post = [nan for _ in xrange(len(self._score.index))]
        for i in xrange(len(self._score.index) - 2):
            post[i + 1] = passing_ind_func((self._score.iloc[i],
                                            self._score.iloc[i + 1],
                                            self._score.iloc[i + 2]))

        # Add post for the final two offsets in the piece. They obviously can't be suspensions,
        # since they wouldn't  be prepared or resolved. (Make sure we use the same index as the
        # other rows, or we'll have empty columns in the output).
        for i in [0, -1]:
            post[i] = pandas.Series([_PASS_NODISS_LABEL for _ in xrange(len(post[1]))],
                                    index=post[1].index)

        # Convert from the list of Series into a DataFrame. Each inputted Series becomes a row.
        post = pandas.DataFrame({j: post[i] for i, j in enumerate(self._score.index)}).T

        # the part names are the column names
        post = self.make_return(list(post.columns), [post[i] for i in post.columns])
        return pandas.concat(objs=[self._score, post], axis=1, join='outer')

class NotaCambiataIndexer(indexer.Indexer):
    # TODO: NOTE: TEST: this whole indexer is untested
    """
    Mark dissonant intervals as a nota cambiata or another dissonance.

    Inputted results from the :mod:`interval` module require the same settings as were given to
    the :class:`DissonanceIndexer.
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = []
    default_settings = {}

    # Text for the RuntimeError raised when a score has fewer than 4 event offsets.
    _TOO_SHORT_ERROR = u'NotaCambiataIndexer: input must have at least 4 events'

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index. You must provide a
            :class:`DataFrame` with results from the
            :class:`~vis.analyzers.indexers.interval.IntervalIndexer`, the
            :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`, and the
            :class:`DissonanceIndexer. The :class:`DataFrame` may contain results from additional
            indexers, which will be ignored.
        :type score: :class:`pandas.DataFrame`
        :param settings: This indexer has no settings, so this is ignored.
        :type settings: NoneType

        .. warning:: The :class:`NotaCambiataIndexer` requires the results of the
            :class:`IntervalIndexer` to have been "forward filled," or there will be errors. Do not
            "forward fill" other indices.

        .. note:: The :meth:`run` method will raise a :exc:`KeyError` if ``score`` does not contain
            results from the required indices.

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        :raises: :exc:`RuntimeError` if the ``score`` argument has fewer than four event offsets,
            which is the minimum required for the completion of the nota cambiata figure.
            An exception here prevents an error later.
        """
        super(NotaCambiataIndexer, self).__init__(score, None)
        if len(score.index) < 4:
            raise RuntimeError(NotaCambiataIndexer._TOO_SHORT_ERROR)
        self._indexer_func = cambiata_ind_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` with nota cambiatas labeled *and* all inputted indices.
        :rtype: :class:`pandas.DataFrame`

        :raises: :exc:`KeyError` if the ``score`` given to the constructor was an
            improperly-formatted :class:`DataFrame` (e.g., it does not contain results of the
            required indexers, or the columns do not have a :class:`MultiIndex`).
        """
        # NB: it's actually cambiata_ind_func() that raises the KeyError

        # this avoids the list's reallocation penalty if we used append()
        post = [nan for _ in xrange(len(self._score.index))]
        for i in xrange(len(self._score.index) - 3):
            post[i + 1] = cambiata_ind_func((self._score.iloc[i],
                                            self._score.iloc[i + 1],
                                            self._score.iloc[i + 2],
                                            self._score.iloc[i + 3]))

        # Add post for the final two offsets in the piece. They obviously can't be nota cambiatas,
        # since they wouldn't  be prepared or resolved. (Make sure we use the same index as the
        # other rows, or we'll have empty columns in the output).
        for i in [0, -1, -2]:   # TODO: adjust to the four-event window size of nota cambiatas
            post[i] = pandas.Series([_CAMB_NODISS_LABEL for _ in xrange(len(post[1]))],
                                    index=post[1].index)

        # Convert from the list of Series into a DataFrame. Each inputted Series becomes a row.
        post = pandas.DataFrame({j: post[i] for i, j in enumerate(self._score.index)}).T

        # the part names are the column names
        post = self.make_return(list(post.columns), [post[i] for i in post.columns])
        return pandas.concat(objs=[self._score, post], axis=1, join='outer')

class ReconciliationIndexer(indexer.Indexer):
    # TODO: NOTE: TEST: this whole indexer is untested
    """
    Reconcile the results from the three dissonance indexers (:class:`SuspensionIndexer`,
    :class:`NeighbourNoteIndexer`, and :class:`PassingNoteIndexer`).

    This means:
    * dissonances are placed into single voices rather than voice pairs,
    * dissonances categorized as "other" are ignored if another indexer has a better classification,
    * a dissonance classified by more than one indexer is marked as both dissonances.

    The dissonance indexers must therefore output well-classified results as a string where a colon
    separates the voice with a dissonant note and the note's classification (e.g., ``'0:UN'`` for
    an upper neighbour note in the highest voice). For each "other" dissonance, we defer to the
    relevant module-level private constants: :const:`_SUSP_OTHER_LABEL`, :const:`_SUSP_NEIGH_LABEL`,
    and :const:`_SUSP_PASS_LABEL`. These are usually set to ``'o'``, but they should always be a
    string (and never :const:`numpy.NaN`, which will cause errors).

    .. note:: All the dissonance indexers must have the same part combinations. That is, they must
        have been generated from the same piece.
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = []
    default_settings = {}

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index. You must provide a
            :class:`DataFrame` with results from the :class:`SuspensionIndexer`,
            :class:`NeighbourNoteIndexer`, and :class:`PassingNoteIndexer`. The :class:`DataFrame`
            may contain results from additional indexers, which will be ignored.
        :type score: :class:`pandas.DataFrame`
        :param settings: This indexer has no settings, so this is ignored.
        :type settings: NoneType

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        """
        super(ReconciliationIndexer, self).__init__(score, None)
        self._indexer_func = reconciliation_func

    def run(self):
        """
        Make a new index of the piece.

        :returns: A :class:`DataFrame` with dissonance classifications reconciled as above.
        :rtype: :class:`pandas.DataFrame`

        .. note:: The returned :class:`DataFrame` only includes the results of this indexer. Any
            other indexers given to :meth:`__init__` are omitted from the return value.
        """
        results = {}
        for i, jay in self._score.iterrows():
            print('--> offset is %s' % i)  # DEBUG
            results[i] = self._indexer_func(jay)
        results = pandas.DataFrame(results).T
        results.columns = pandas.MultiIndex.from_tuples([('dissonance.ReconciliationIndexer', x) for x in results.columns])
        return results