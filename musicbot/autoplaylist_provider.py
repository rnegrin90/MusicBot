import uuid

from musicbot.config import Config, ConfigDefaults
allow_requests = True
from azure.cosmosdb.table.tableservice import TableService

from musicbot.utils import load_file, remove_from_file, append_file


class AzureTableProvider:
    def __init__(self, account_name, key, table_name):
        self.target_table = table_name

        if not account_name or not key:
            raise Exception('Account or key not specified')

        self.table_service = TableService(account_name=account_name, account_key=key)
        self.table_service.create_table(self.target_table)

    def get_all(self):
        return self.table_service.query_entities(self.target_table)

    def remove(self, item):
        query_str = "Link eq '%s'" % item
        tasks = self.table_service.query_entities(self.target_table, filter=query_str)
        if any(tasks):
            for task in tasks:
                self.table_service.delete_entity(self.target_table, task.PartitionKey, task.RowKey)
                return True
        return False

    def add(self, item):
        track = {
            'PartitionKey': 'MusicBotEntry',
            'RowKey': str(uuid.uuid4()),
            'Link': item
        }
        self.table_service.insert_entity(self.target_table, track)


class PlaylistProvider:
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = ConfigDefaults.options_file

        self.config = Config(config_file)

        self.azure_provider = None
        if self.config.remote_auto_playlist:
            try:
                self.azure_provider = AzureTableProvider(self.config.azure_account, self.config.azure_key, self.config.table_name)
            except Exception:
                pass

    def get_track_list(self):
        if self.azure_provider:
            tracks = self.azure_provider.get_all()
            if any(tracks):
                return [t.Link for t in tracks]
            else:
                video_list = load_file(self.config.auto_playlist_file)
                self.backup(video_list)
                return video_list
        else:
            return load_file(self.config.auto_playlist_file)

    def remove_track(self, track):
        if self.azure_provider:
            return self.azure_provider.remove(track)
        else:
            return remove_from_file(self.config.auto_playlist_file, track)

    def add_track(self, track):
        if self.azure_provider:
            return self.azure_provider.add(track)
        else:
            return append_file(self.config.auto_playlist_file, track)

    def backup(self, track_list):
        for track in track_list:
            self.azure_provider.add(track)
