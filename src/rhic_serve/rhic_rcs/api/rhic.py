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


from django.conf import settings
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization

from certutils.certutils import CertFileUtils
from splice.common import certs
from splice.common.auth import X509CertificateAuthentication

from rhic_serve.common.api import RestResource
from rhic_serve.rhic_rcs.models import RHIC


class RHICRcsResource(RestResource):

    class Meta(RestResource.Meta):
        queryset = RHIC.objects.all()
        authentication = X509CertificateAuthentication(
            certs.get_splice_server_identity_ca_pem())
        authorization = ReadOnlyAuthorization()
        detail_uri_name = 'uuid'
        # This class is likely to be subclassed, and we want the resource name
        # preserved.
        resource_name = 'rhicrcs'
        filtering = {
            'created_date': ['gte', 'gt', 'lte', 'lt', 'range'],
            'modified_date': ['gte', 'gt', 'lte', 'lt', 'range'],
            'deleted_date': ['gte', 'gt', 'lte', 'lt', 'range'],
            'deleted': ['exact'],
        }
        max_limit = 0

    def alter_list_data_to_serialize(self, request, data):
        """
        """
        return data
