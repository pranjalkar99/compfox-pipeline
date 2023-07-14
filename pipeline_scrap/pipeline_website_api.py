# main.py

from imports import *
from utils import *
from configs import *

@pipe.get("/")
async def root():
    return {"message": "Go to /docs for the API documentation."}

@pipe.get("/start-batch")
async def start_batch():
    os.mkdir("pdfs")
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    a_tags = soup.find_all('a')
    for a in a_tags:
        try:
            if a.get('href').endswith('.pdf'):
                link =  "https://www.dir.ca.gov" +a.get('href')
                download_pdf(link, "pdfs/"+a.get_text()+".pdf")
                break
            # print("Text:", a.get_text())
            # print()
        except:
            logging.warning("Unable to read -> " + a.get_text())
    
    os.remove("pdfs")
    return {"message": "Batch started."}

if __name__ == "__main__":
    uvicorn.run(pipe, port=8000)