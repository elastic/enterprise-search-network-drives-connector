#
# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. Licensed under the Elastic License 2.0;
# you may not use this file except in compliance with the Elastic License 2.0.
#
"""This module allows to run a full sync against a Network Drives.

    It will attempt to sync absolutely all documents that are available in the
    third-party system and ingest them into Enterprise Search instance.
"""
from datetime import datetime

from .base_command import BaseCommand
from .indexer import start
from .checkpointing import Checkpoint
from .constant import DATETIME_FORMAT

INDEXING_TYPE = "full"


class FullSyncCommand(BaseCommand):
    def execute(self):
        config = self.config
        logger = self.logger
        workplace_search_client = self.workplace_search_client
        network_drive_client = self.network_drive_client
        indexing_rules = self.indexing_rules
        storage_obj = self.local_storage
        current_time = (datetime.utcnow()).strftime(DATETIME_FORMAT)
        checkpoint = Checkpoint(config, logger)
        drive = config.get_value("network_drive.server_name")

        time_range = {"start_time": config.get_value("start_time"), "end_time": current_time}

        start(time_range, config, logger, workplace_search_client, network_drive_client, indexing_rules, storage_obj)
        checkpoint.set_checkpoint(current_time, INDEXING_TYPE, drive)
