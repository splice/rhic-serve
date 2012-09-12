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


from datetime import datetime
from dateutil.tz import tzutc

from django.conf import settings

# Given all the base classes, fields, etc, that we need to make use of from
# mognoengine, it's easiest to just use import *
from mongoengine import *
from mongoengine import signals
from mongoengine.queryset import QuerySet

from rhic_serve.common import cert_utils
from rhic_serve.common.models import *

import uuid

class Product(EmbeddedDocument):

    support_level_choices = {
        'l1-l3': 'L1-L3',
        'l3': 'L3-only',
        'ss': 'SS',
    }

    sla_choices = {
        'std': 'Standard',
        'prem': 'Premium',
        'na': 'N/A',
    }

    # Product name
    name = StringField(required=True)
    # Unique product identifier
    engineering_ids = ListField(required=True)
    # Quantity 
    quantity = IntField(required=True)
    # Product support level
    support_level = StringField(required=True, choices=support_level_choices.keys())
    # Product sla
    sla = StringField(required=True, choices=sla_choices.keys())


class Contract(EmbeddedDocument):
    # Unique Contract identifier
    contract_id = StringField(unique=True, required=True)
    # List of products associated with this contract
    products = ListField(EmbeddedDocumentField(Product))


class Account(Document):

    meta = {
        'queryset_class': BaseQuerySet,
    }

    # Unique account identifier
    account_id = StringField(unique=True, required=True)
    # Human readable account name
    login = StringField(unique=True, required=True)
    # List of contracts associated with the account.
    contracts = ListField(EmbeddedDocumentField(Contract))


class RHIC(Document):

    meta = {
        # Override collection name, otherwise we get r_h_i_c.
        'collection': 'rhic',
        'queryset_class': BaseQuerySet,
    }

    # Human readable name
    name = StringField(unique=True)
    # Unique account identifier tying the RHIC to an account.
    account_id = StringField()
    # Contract associated with the RHIC.
    contract = StringField()
    # Support Level associated with the RHIC.
    support_level = StringField()
    # SLA (service level availability) associated with the RHIC.
    sla = StringField()
    # UUID associated with the RHIC.
    uuid = UUIDField()
    # List of Products associated with the RHIC.
    products = ListField()
    # List of Engineering Id's associated with the RHIC.
    engineering_ids = ListField()
    # Public cert portion of the RHIC.
    public_cert = FileField()
    # Date RHIC was created
    created_date = DateTimeField(default=datetime.now(tzutc()))
    # Date RHIC was last modified
    modified_date = DateTimeField(default=datetime.now(tzutc()))

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """
        pre_save signal hook.
        """
        # Verify a UUID is always set before we save.  If one is not, generate a
        # new one and set it.
        if not document.uuid:
            document.uuid = cls._generate_uuid()

        # Set name
        if not document.name:
            document.name = document._generate_name()

        # Generate a certificate and private key for this RHIC.
        if not document.public_cert:
            public_cert, private_key = cert_utils.generate(
                str(document.uuid), settings.CA_CERT_PATH, settings.CA_KEY_PATH,
                settings.CERT_DAYS)
            document.public_cert.new_file()
            document.public_cert.write(public_cert)
            document.public_cert.close()

            # private key is saved as an attribute on the document, but it is
            # not a field.  It will not be kept after this instance is GC'd.
            document.private_key = private_key

    @classmethod
    def _generate_uuid(cls):
        """
        Generate a random UUID.
        """
        return uuid.uuid4()

    def _generate_name(self):
        """
        Generates a nice human readable name based on other RHIC fields.
        """
        return "%s-%s-%s-%s" % (self.account_id, self.contract, self.sla,
            self.support_level)


# Signals
signals.pre_save.connect(RHIC.pre_save, sender=RHIC)

