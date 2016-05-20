#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/active_voices.py
# Purpose:                Active voices indexer
#
# Copyright (C) 2016 Marina Borsodi-Benson
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
.. codeauthor:: Marina Borsodi-Benson <marinaborsodibenson@gmail.com>

"""

import music21
from vis.analyzers import indexer
import pandas
import pdb


def indexer1(x):

    if x == 'Rest' or isinstance(x, float):
        return 0
    else:
        return 1


class ActiveVoicesIndexer(indexer.Indexer):
    """
    Class that indexer the number of voices active at each offset.
    """

    required_score_type = 'pandas.DataFrame'
    possible_settings = ['attacked', 'show_all']
    """
    :keyword 'attacked': When true, only counts the voices that are attacking at each offset. Defaults to false.
    :type 'attacked': boolean
    :keyword 'show_all': When true, shows the results at all offsets, even if there is not change. Defaults to false.
    :type 'show_all': boolean
    """
    default_settings = {'attacked': False, 'show_all': False}

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index.
        :type score: :class:`pandas.DataFrame`
        :param settings: All the settings required by this indexer.
        :type settings: dict or None

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        """

        self._settings = self.default_settings
        if settings is not None:
            self._settings.update(settings)

        if self._settings['attacked']:
            self.score = score
        else:
            self.score = score.fillna(method='ffill')

        super(ActiveVoicesIndexer, self).__init__(score, None)

    def run(self):
        """
        :returns: Make a new index of the active voices in the piece.
        :rtype: :class:`pandas.DataFrame`
        
        PLEASE ADD (since it will become part of the auto-generated documentation):
        **Example:**
        
        
        """

        post = self.score.applymap(indexer1)
        most = post.sum(axis=1)

        indices = most.index.tolist()
        if not self._settings['show_all']:
            for n, ind in reversed(list(enumerate(most))):
                if ind == most.iloc[n - 1]:
                    most = most.drop(indices[n])

        result = pandas.DataFrame({'Active Voices': most})
        return self.make_return(result.columns.values, [result[name] for name in result.columns])
