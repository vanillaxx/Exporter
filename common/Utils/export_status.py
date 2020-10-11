from enum import Enum


class ExportStatus(Enum):
    SUCCESS = 1
    FAILURE = 2

    def get_message(self, file_name=None):
        if self is ExportStatus.SUCCESS and file_name is not None:
            return f'Data exported to {file_name}'
        else:
            return 'There is no data for such company'
