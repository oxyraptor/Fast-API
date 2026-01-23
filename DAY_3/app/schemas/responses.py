from pydantic import BaseModel
from typing import Dict

class UploadResponse(BaseModel):
    dataset_id : str
    filename: str

class SummaryResponse(BaseModel):
    rows : int
    coloums : int
    coloums_type : dict[str, str]

class MissingValuesResponse(BaseModel):
    missing_values : Dict[str, int]

class CorelationMatrixResponse(BaseModel):
    corelation : Dict[str, Dict[str,float]]

class GetFilenameResponse(BaseModel):
    filename : str
