#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/experimenters/aggregator.py
# Purpose:                Aggregating experimenters.
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
Aggregating experimenters.
"""

import pandas
from vis.analyzers import experimenter


class ColumnAggregator(experimenter.Experimenter):
    """
    Experiment that aggregates data from all columns of a DataFrame, a list of DataFrames, or a
    list of Series, into a single Series. Aggregation is done through addition. If a DataFrame has
    a column with the name u'all', it will *not* be included in the aggregation.
    """

    required_indices = []
    required_experiments = []
    possible_settings = []  # list of strings
    default_settings = {}  # keys are strings, values are anything

    def __init__(self, index, settings=None):
        """
        Create a new ColumnAggregator.

        Parameters
        ==========
        :param index: The data to aggregate. You should ensure the row index of each pandas object
            can be sensibly combined. The data should be numbers. If a DataFrame has a column with
            the name u'all', it will *not* be included in the aggregation.
        :type index: pandas.DataFrame or list of pandas.DataFrame or list of pandas.Series

        :param settings: dict
            A dict of all the settings required by this Experimenter. All required settings should
            be listed in subclasses. Default is {}.
        """
        super(ColumnAggregator, self).__init__(index, None)

    def run(self):
        """
        Run the ColumnAggregator experiment.

        Returns
        =======
        :returns: A Series with an index that is the combination of all indices of provided pandas
            objects, and the value is the sum of all the values in the pandas objects.
        :rtype: pandas.Series
        """
        # make sure we have a single DataFrame
        if isinstance(self._index, list):
            if isinstance(self._index[0], pandas.DataFrame):
                self._index = [ColumnAggregator(x).run() for x in self._index]
            # combine the list-of-Series into a DataFrame
            self._index = pandas.DataFrame(dict([(i, x) for i, x in enumerate(self._index)]))
        # make the sum aggregation
        return self._index.select(lambda x: x != u'all', axis=1).sum(axis=1, skipna=True)
