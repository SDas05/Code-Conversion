from typing import List
from pathlib import Path
from app.input.file_metadata import FileMetadata

class PreprocessingQueue:
    """
    Manages a queue of files to be preprocessed.
    """

    def __init__(self):
        self.queue: List[FileMetadata] = []
    
    def enqueue(self, file_metadata: FileMetadata):
        self.queue.append(file_metadata)
        self.queue.sort(key= lambda x:x.priority)

    def get_next_file(self) -> FileMetadata:
        if self.queue:
            return self.queue.pop(0)
        raise IndexError("No files exist in queue.")
    
    def peek_all(self) -> List[FileMetadata]:
        return self.queue.copy()
    
    def clear(self):
        return self.queue.clear()