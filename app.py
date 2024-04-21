from fastapi import File, UploadFile, Request, FastAPI, HTTPException, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, StreamingResponse
from zipfile import ZipFile
import dicom2nifti
import shutil
import subprocess
from glob import glob
import tempfile
import time
import os


templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix='/v1/modelapi')


@router.get("/")
def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/upload")
def upload(request: Request, file: UploadFile = File(...)):
    
    # TODO: Save upload file
    work_dir = tempfile.TemporaryDirectory()
    work_dir_name = work_dir.name
    upload_file = os.path.join(work_dir_name, file.filename)
    try:
        contents = file.file.read()
        with open(upload_file, "wb") as f:
            f.write(contents)
    except Exception as e:
        print(e)
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    # TODO: Unzip file
    dicom_directory = f"{work_dir_name}/dicom"
    with ZipFile(upload_file) as zObject:
        zObject.extractall(path=dicom_directory)
    print(f"Dicom files: {os.listdir(dicom_directory)}")

    # TODO: Dicom to nifti
    dicom2nifti.convert_directory(dicom_directory, work_dir_name)

    # TODO: Run segment
    nifti_file = glob(f"{work_dir_name}/*.nii*")[0]
    print(f"Segment on nifti file: {nifti_file}")
    model_type = "medium"
    subprocess.run(f"export CUDA_VISIBLE_DEVICES=0 && skellytour -i {nifti_file} -o {work_dir_name}/segment -m {model_type} --overwrite", shell=True)

    # TODO: Nifti to mesh
    segment_file = glob(f"{work_dir_name}/segment/*postprocessed.nii*")[0]
    print(f"Convert mesh on nifti file: {segment_file}")
    mesh_file = "_".join([nifti_file.split('.')[0], str(int(time.time()))]) + ".stl"
    subprocess.run(f"./nii2mesh/nii2mesh {segment_file} -v 1 -i b {mesh_file}", shell=True)

    # Clean up
    # work_dir.cleanup()
    print(f"Work dir: {work_dir_name}")
    shutil.copy(mesh_file, f"/tmp/{os.path.basename(mesh_file)}")
    return templates.TemplateResponse("display.html", {"request": request,  "file_name": os.path.basename(mesh_file)})


@router.get("/download/{filename}")
def download_file(filename: str, request: Request):
    file_path = os.path.join("/tmp", filename).replace('..', '.')
    ext = os.path.splitext(file_path)[-1]
    if ext not in ['.stl']:
        raise
    return FileResponse(file_path, media_type="application/octet-stream", filename=os.path.basename(file_path))


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8081)
