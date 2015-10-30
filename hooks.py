"""Post save hook for Experiments so that ACLs are created for the
appropriate EPN group
"""

import logging
from django.contrib.auth.models import Group

from django.db.models.signals import post_save
from django.dispatch import receiver
from tardis.tardis_portal.models import (
    Experiment, ExperimentParameter, ObjectACL, ParameterName, Schema)
from tardis.tardis_portal.auth.localdb_auth import django_group

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ExperimentParameter)
def add_epn_group_acl(sender, **kwargs):
    try:
        par_name = ParameterName.objects.get(
            name='EPN', schema=Schema.objects.get(
                namespace='http://www.tardis.edu.au/schemas/as/'
                          'experiment/2010/09/21'))
    except (ParameterName.DoesNotExist, Schema.DoesNotExist):
        return
    exp_par = kwargs['instance']
    if exp_par.name != par_name:
        return
    exp = exp_par.parameterset.experiment
    try:
        epn = exp_par.string_value
        # create vbl group
        acl = ObjectACL.objects.filter(
            content_type=exp.get_ct(),
            object_id=exp.id,
            pluginId='vbl_group',
            entityId=epn,
            canRead=True,
            aclOwnershipType=ObjectACL.SYSTEM_OWNED)
        if len(acl) == 0:
            acl = ObjectACL(
                content_type=exp.get_ct(),
                object_id=exp.id,
                pluginId='vbl_group',
                entityId=epn,
                canRead=True,
                aclOwnershipType=ObjectACL.SYSTEM_OWNED)
            acl.save()
    except Exception:
        logger.exception('trouble creating EPN ACL')

    try:
        beamline_group = "BEAMLINE_MX"
        group, created = Group.objects.get_or_create(name=beamline_group)
        # beamline group
        ObjectACL.objects.get_or_create(
            content_type=exp.get_ct(),
            object_id=exp.id,
            pluginId=django_group,
            entityId=str(group.id),
            canRead=True,
            aclOwnershipType=ObjectACL.SYSTEM_OWNED)

        # finally, always add acl for admin group
        group, created = Group.objects.get_or_create(name='admin')
        ObjectACL.objects.get_or_create(
            content_type=exp.get_ct(),
            object_id=exp.id,
            pluginId=django_group,
            entityId=str(group.id),
            isOwner=True,
            canRead=True,
            aclOwnershipType=ObjectACL.SYSTEM_OWNED)
    except Exception:
        logger.exception('trouble creating beamline and admin ACLs')
