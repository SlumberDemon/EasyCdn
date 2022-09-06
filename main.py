import os

import fastapi
from deta import Drive
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

pages = Jinja2Templates(directory="pages")
files = Drive("EasyCdn")
app = fastapi.FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=fastapi.responses.HTMLResponse)
async def home(request: fastapi.Request):
    return pages.TemplateResponse("home.html", {"request": request})


@app.post("/upload")
def upload_file(
    request: fastapi.Request,
    password: str,
    file: fastapi.UploadFile = fastapi.File(...),
):
    if password == f"{os.getenv('PASSWORD')}":
        name = files.put(file.filename.replace(" ", "_"), file.file)
        return {
            "file": f"{request.url.scheme}://{request.url.hostname}/{name}",
        }
    else:
        return {"Error": "Password incorrect"}


@app.get("/{name}")
def cdn(name: str):
    img = files.get(name)
    ext = name.split(".")[1]
    return fastapi.responses.StreamingResponse(
        img.iter_chunks(), media_type=f"image/{ext}"
    )
