from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
from mangum import Mangum

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def heading_to_markdown(tag):
    level = int(tag.name[1])
    return f"{'#' * level} {tag.get_text(strip=True)}"

@app.get("/api/outline")
def get_country_outline(country: str = Query(...)):
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "Could not fetch Wikipedia page"}

    soup = BeautifulSoup(response.content, "html.parser")
    content_div = soup.find("div", {"class": "mw-parser-output"})

    if not content_div:
        return {"error": "Could not find content section"}

    headings = content_div.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    markdown_outline = "## Contents\n\n" + f"# {country.title()}\n\n"
    for tag in headings:
        markdown_outline += heading_to_markdown(tag) + "\n\n"

    return {"country": country, "markdown_outline": markdown_outline}

# Wrap with Mangum for Vercel
handler = Mangum(app)
