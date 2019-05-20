# -*- coding: utf-8 -*-

from operator import methodcaller

from bika.lims import api
from senaite.impress.interfaces import IStorage
from zope.interface import implements


class StorageAdapter(object):
    """Storage adapter for PDF reports
    """
    implements(IStorage)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_primary_report(self, objs):
        """Get the primary report
        """
        # sort the objects by created to have the most recent object first
        objs = sorted(objs, key=methodcaller("created"))
        return objs[0]

    def store_multireports_individually(self):
        """Returns the configured setting from the registry
        """
        store_individually = api.get_registry_record(
            "senaite.impress.store_multireports_individually")
        return store_individually

    def store(self, pdf, html, uids, metadata=None):
        """Store the PDF

        :param pdf: generated PDF report (binary)
        :param html: report HTML (string)
        :param uids: UIDs of the objects contained in the PDF
        :param metadata: dict of metadata to store
        """

        if metadata is None:
            metadata = {}

        # get the contained objects
        objs = map(api.get_object_by_uid, uids)

        # handle primary object storage
        if self.store_multireports_individually():
            # reduce the list to the primary object only
            objs = [self.get_primary_report(objs)]

        # generate the reports
        reports = []
        for obj in objs:
            report = self.create_report(obj, pdf, html, uids, metadata)
            reports.append(report)

        return reports

    def create_report(self, parent, pdf, html, uids, metadata):
        """Create a new report object

        :param parent: parent object where to create the report inside
        :returns: ARReport
        """
        report = api.create(parent, "ARReport")
        report.edit(
            title=api.get_id(report),
            AnalysisRequest=api.get_uid(parent),
            Pdf=pdf,
            Html=html,
            ContainedAnalysisRequests=uids,
            Metadata=metadata)

        return report
