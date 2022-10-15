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
    file: fastapi.UploadFile,
):
    if password == os.getenv('PASSWORD'):
        name = files.put(file.filename.replace(" ", "_"), file.file)
        return {
            "file": f"{request.url.scheme}://{request.url.hostname}/{name}",
        }
    else:
        return {"error": "Password incorrect"}


@app.get("/{name}")
def cdn(name: str):
    img = files.get(name)
    if img is None:
        raise fastapi.HTTPException(status_code=404)
    ext = name.split(".")[-1]
    return fastapi.responses.Response(
        img.read(),
        media_type=f"image/{ext}",
        # Cache for 24 hours.
        headers={"Cache-Control": "public, max-age=86400"},
    )


@app.get("/embed/{name}")
def cdn_embed(request: fastapi.Request, name: str):
    return fastapi.responses.HTMLResponse(
        f"""
        <meta name="twitter:card" content="summary_large_image">
        <meta property="og:title" content="{name}"/>
        <meta property="og:type" content="website"/>
        <meta property="og:image" content="{request.url.scheme}://{request.url.hostname}/{name}"/>
        <meta property="og:url" content="{request.url.scheme}://{request.url.hostname}/"/>
        <meta name="url" content="{request.url.scheme}://{request.url.hostname}/">
        <meta name="theme-color" content="#9ECFC2">
        <img alt="image" src="{request.url.scheme}://{request.url.hostname}/{name}">
        """
    )
