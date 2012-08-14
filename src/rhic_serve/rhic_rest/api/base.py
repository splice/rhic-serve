# -*- coding: utf-8 -*-
#
# Copyright © 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from tastypie_mongoengine.resources import MongoEngineResource

class RestResource(MongoEngineResource):
    """
    Base class for the rhic_rest application.

    Will override some functionality from MongoEngineResource.
    """

    def alter_list_data_to_serialize(self, request, data):
        """
        While the meta dictionary in the standard MongoEngineResource is
        valuable for things like pagination, counts, etc., we just want the
        standard response to be the list of resources requested.

        TODO:
        We need to make the information in meta available on demand via a query
        parameter.

        This method removes a meta key from the data dictionary, and turns data
        into a list of resources.
        """
        if isinstance(data, dict):
            if 'meta' in data:
                data.pop('meta')
            if 'objects' in data:
                data = data['objects']

            return data



