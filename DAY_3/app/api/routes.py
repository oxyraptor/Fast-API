from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter
import uuid
import pandas as pd
import os
from app.schemas.responses import MissingValuesResponse, GetFilenameResponse,UploadResponse, SummaryResponse, CorelationMatrixResponse
router = APIRouter(prefix="/dataset", tags=["dataset"])


DATASET_DIR = r"D:\programs\API\fastapi\DAY_3\app\storage\dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

@router.post("/upload", response_model=UploadResponse)
async def upload_file(File:UploadFile = File(...)):
    if not File.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload CSV file")
    dataset_id = str(uuid.uuid4())
    # Save as {uuid}_{filename} to preserve original name
    file_path = os.path.join(DATASET_DIR, f"{dataset_id}_{File.filename}")

    with open(file_path, "wb") as f:
        f.write(await File.read())

    return{
        "dataset_id": dataset_id,
        "filename": File.filename
    }

@router.get("/Load")
def get_file_name( ):
    file = os.listdir(DATASET_DIR)
    csv_files = [f for f in file if f.endswith(".csv")]
    return {
        "file": csv_files
    }


from app.services.analytics import load_dataset,Summary, missing_values, corelation_matrix

def get_file_path(dataset_id: str):
    # Search for any file starting with the dataset_id
    for f in os.listdir(DATASET_DIR):
        if f.startswith(dataset_id) and f.endswith(".csv"):
            return os.path.join(DATASET_DIR, f)
    raise HTTPException(status_code=404, detail="Dataset not found")

@router.get("/{dataset_id}/Summary", response_model=SummaryResponse)
def get_summary(dataset_id: str):
    path = get_file_path(dataset_id)
    df = load_dataset(path)
    return Summary(df) 

@router.get("/{dataset_id}/missing_values", response_model=MissingValuesResponse)
def get_missing_values(dataset_id: str):
    path = get_file_path(dataset_id)
    df = load_dataset(path)
    return missing_values(df)

@router.get("/{dataset_id}/corelation_matrix", response_model=CorelationMatrixResponse)
def get_corelation_matrix(dataset_id : str):
    path = get_file_path(dataset_id)
    df =load_dataset(path)
    return corelation_matrix(df)




