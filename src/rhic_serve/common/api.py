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

from tastypie.authentication import (BasicAuthentication, 
    MultiAuthentication, SessionAuthentication)
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie_mongoengine.resources import MongoEngineResource


class RestSerializer(Serializer):
    """
    Class for overriding various aspects of the default Tastypie Serializer
    class.
    """

    def format_datetime(self, data):
        """
        By default, Tastypie's serializer serializes all datetime objects as
        naive (no timezone info).  I'm not sure why this is the case.

        There's a patch, but it has not been merged into master Tastypie:
        https://github.com/toastdriven/django-tastypie/commit/542d365d7d975a90c64c4c375257e5bc4b3b220a
        """
        return data.isoformat()


class RestResource(MongoEngineResource):
    """
    Base class for the rhic_rest application.

    Will override some functionality from MongoEngineResource.
    """

    class Meta:
        """
        Common base Rest Resource options.
        """
        # Make sure we always get back the representation of the resource back
        # on a POST.
        always_return_data = True

        # All Resources require basic authentication (for now).
        authentication = MultiAuthentication(SessionAuthentication(),
            BasicAuthentication())

        # Use our serializer for all resources
        serializer = RestSerializer()

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

    def dehydrate_resource_uri(self, bundle):
        """
        Override all resource uri's with their absolute (protocol, host, port,
        path) counterparts.
        """
        resource_uri = super(RestResource, self).dehydrate_resource_uri(bundle)
        return bundle.request.build_absolute_uri(resource_uri)

    def determine_format(self, request):
        """
        Always return json.  Makes it such that specifying the format=json
        query parameter is not required as it typically is by tastypie.
        """
        return 'application/json'

    def full_hydrate(self, bundle):
        """
        Override to just call tastypie's full_hydrate.

        django-tastypie-mongoengine does a lot of extra checks that make some
        assumptions that break things in their full_hydrate method.
        """
        return ModelResource.full_hydrate(self, bundle)
