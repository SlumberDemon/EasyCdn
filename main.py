import os

import fastapi
from deta import Drive
from fastapi.templating import Jinja2Templates

pages = Jinja2Templates(directory="pages")
cdn = os.getenv("NAME")
files = Drive("EasyCdn")
app = fastapi.FastAPI()


@app.get("/", response_class=fastapi.responses.HTMLResponse)
async def home(request: fastapi.Request):
    return pages.TemplateResponse("home.html", {"request": request})


@app.post("/upload")
def upload_file(password: str, file: fastapi.UploadFile = fastapi.File(...)):
    if password == str(os.getenv("PASSWORD")):
        name = files.put(file.filename.replace(" ", "_"), file.file)
        return {
            "file": f"https://{cdn}.deta.dev/{name}",
            "embed": f"https://{cdn}.deta.dev/embed/{name}",
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


@app.get("/embed/{name}")
def embeded_image(name: str):
    return fastapi.responses.HTMLResponse(
        f"""
        <meta name="twitter:card" content="summary_large_image">
        <meta property="og:title" content="{cdn} | Hosted with EasyCdn"/>
        <meta property="og:type" content="website"/>
        <meta property="og:image" content="https://{cdn}.deta.dev/{name}"/>
        <meta property="og:url" content="https://{cdn}.deta.dev"/>
        <meta name="url" content="https://{cdn}.deta.dev">
        <meta name="theme-color" content="#9ECFC2">
        <img alt="File" src="https://{cdn}.deta.dev/{name}">
        """
    )
