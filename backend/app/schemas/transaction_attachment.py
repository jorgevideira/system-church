from datetime import datetime

from pydantic import BaseModel


class TransactionAttachmentResponse(BaseModel):
    id: int
    transaction_id: int
    original_filename: str
    mime_type: str
    original_size: int
    compressed_size: int
    compression: str
    created_at: datetime

    model_config = {"from_attributes": True}
