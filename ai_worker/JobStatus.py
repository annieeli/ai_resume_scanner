from enum import StrEnum

class JobStatus(StrEnum):
    UNKNOWN = "Unknown"
    QUEUED = "Queued"
    EXTRACTING_TEXT = "ExtractingText"
    ANALYZING = "Analyzing"
    COMPLETED = "Completed"
    FAILED = "Failed"