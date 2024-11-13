"""## Setup"""

!pip install -U -q "google-generativeai>=0.8.2"

!apt-get update -qq
!apt-get install -qqy wget unzip
!pip install selenium
!wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt install ./google-chrome-stable_current_amd64.deb

import os
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import time
from IPython.display import display
from IPython.display import Markdown
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from IPython.display import Image, display
from bs4 import BeautifulSoup
import io

genai.configure(api_key='key')

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro-002",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
  ]
)

# BBC Technology news section URL
base_url = 'https://www.bbc.com'
tech_url = f'{base_url}/innovation/artificial-intelligence'

def driversetup():
    options = webdriver.ChromeOptions()
    #run Selenium in headless mode
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    #overcome limited resource problems
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("lang=en")
    options.add_argument('--disable-gpu')
    #open Browser in maximized mode
    options.add_argument("start-maximized")
    #disable infobars
    options.add_argument("disable-infobars")
    #disable extension
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

    return driver

# Set up Chrome options for Colab
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--remote-debugging-port=9222')
options.add_argument('--disable-software-rasterizer')

# Path to the ChromeDriver in Colab environment
service = Service('/usr/local/bin/chromedriver')

def get_bbc_tech_news():
    driver = driversetup()
    driver.get(tech_url)
    time.sleep(3)

    # Parse the fully rendered HTML with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Close the WebDriver after use
    driver.quit()

    # Initialize list to store articles
    articles = []
    links = []
    count = 0

    # Loop through news items in technology section
    for card in soup.select('[data-testid="windsor-card"], [data-testid="london-card"], [data-testid="edinburgh-card"]'):
        # Extract the headline text
        headline_tag = card.select_one('[data-testid="card-headline"]')
        headline = headline_tag.get_text(strip=True) if headline_tag else "No headline"

        # Extract the link
        link_tag = card.select_one('a[data-testid="internal-link"]')
        link = f"https://www.bbc.com{link_tag['href']}" if link_tag else None

        # Extract the highest-resolution image URL from srcset
        image_url = None
        image_tag = card.select_one('img')
        if image_tag and 'srcset' in image_tag.attrs:
            # Parse the srcset attribute to get multiple resolutions
            srcset = image_tag['srcset'].split(',')
            # Extract the URL with the highest resolution
            highest_res = max(srcset, key=lambda x: int(x.split()[-1][:-1]))
            image_url = highest_res.split()[0]  # Get the URL part only
        elif image_tag and 'src' in image_tag.attrs:
            # Fall back to 'src' if 'srcset' is not available
            image_url = image_tag['src']

        # Store the result if both headline and link are present
        if headline and link:
            article_content = get_article_content(link)
            if article_content is None:
                continue
            if link in links:
                continue

            articles.append({
                'headline': headline,
                'link': link,
                'image_url': image_url,
                'content': article_content
            })
            links.append(link)
            count += 1

        if count >= 3:
            break
        time.sleep(1)

    return articles

def get_article_content(article_url):
    """Fetches and returns the main content of the article."""
    response = requests.get(article_url)
    if response.status_code != 200:
        print(f"Failed to retrieve article: {article_url}")
        return "Content not available"

    # Parse the article page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize a list to collect all paragraphs from all sections
    all_paragraphs = []

    # Find all sections with data-component="text-block" and extract paragraphs
    for content_div in soup.select('[data-component="text-block"]'):
        paragraphs = [p.get_text(strip=True) for p in content_div.find_all('p')]
        all_paragraphs.extend(paragraphs)

    # Combine all paragraphs into a single content string
    article_content = "\n".join(all_paragraphs) if all_paragraphs else None

    return article_content

# Run the function and print results
news_articles = get_bbc_tech_news()
for article in news_articles:  # Display the first 3 articles for brevity
    print(f"Headline: {article['headline']}")
    print(f"Link: {article['link']}")
    print(f"Image Link: {article['image_url']}\n")
    print(f"Content:\n{article['content']}\n")
    # Display the image if available
    if article['image_url']:
        try:
            image_response = requests.get(article['image_url'])
            # Convert your image bytes to a displayable format
            image_bytes = io.BytesIO(image_response.content)

            # Display the image inline
            display(Image(data=image_bytes.getvalue()))
            print("\n")
            print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve image: {e}\n")

prompt = "Please summarise and rewrite the news:headline and content for young people (between 7 and 18), we want to have a kids version. The news was scraped by a web crawler, so if there is anything irrelevant, please remove it. Thank you!"

for article in news_articles:  # Display the first 3 articles for brevity
    print(f"Original News Link: {article['link']}")
    print(f"Original Image Link: {article['image_url']}\n")
    contents = f"Here is the news:\nHeadline:\n {article['headline']}\nContent:\n{article['content']}\n{prompt}"
    # Call the model and print the response
    response = chat_session.send_message(contents)
    display(Markdown(response.text))
    # Display the image if available
    if article['image_url']:
        try:
            image_response = requests.get(article['image_url'])
            # Convert your image bytes to a displayable format
            image_bytes = io.BytesIO(image_response.content)

            # Display the image inline
            display(Image(data=image_bytes.getvalue()))
            print("\n")
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve image: {e}\n")
    print("-------------------------------------------------------------------\n")

"""## Call `generate_content`"""



"""<table class="tfo-notebook-buttons" align="left">
  <td>
    <a target="_blank" href="https://ai.google.dev/gemini-api/docs"><img src="https://ai.google.dev/static/site-assets/images/docs/notebook-site-button.png" height="32" width="32" />Docs on ai.google.dev</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/google-gemini/cookbook/blob/main/quickstarts"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" />More notebooks in the Cookbook</a>
  </td>
</table>

## [optional] Show the conversation

This section displays the conversation received from Google AI Studio.
"""

# @title Show the conversation, in colab.
import mimetypes

def show_file(file_data):
    mime_type = file_data["mime_type"]

    if drive_id := file_data.get("drive_id", None):
        path = next(
            pathlib.Path(f"/gdrive/.shortcut-targets-by-id/{drive_id}").glob("*")
        )
        name = path
        # data = path.read_bytes()
        kwargs = {"filename": path}
    elif url := file_data.get("url", None):
        name = url
        kwargs = {"url": url}
        # response = requests.get(url)
        # data = response.content
    elif data := file_data.get("inline_data", None):
        name = None
        kwargs = {"data": data}
    elif name := file_data.get("filename", None):
        if not pathlib.Path(name).exists():
            raise IOError(
                f"local file: `{name}` does not exist. You can upload files to "
                'Colab using the file manager ("📁 Files"in the left toolbar)'
            )
    else:
        raise ValueError("Either `drive_id`, `url` or `inline_data` must be provided.")

        print(f"File:\n    name: {name}\n    mime_type: {mime_type}\n")
        return

    format = mimetypes.guess_extension(mime_type).strip(".")
    if mime_type.startswith("image/"):
        image = IPython.display.Image(**kwargs, width=256)
        IPython.display.display(image)
        print()
        return

    if mime_type.startswith("audio/"):
        if len(data) < 2**12:
            audio = IPython.display.Audio(**kwargs)
            IPython.display.display(audio)
            print()
            return

    if mime_type.startswith("video/"):
        if len(data) < 2**12:
            audio = IPython.display.Video(**kwargs, mimetype=mime_type)
            IPython.display.display(audio)
            print()
            return

    print(f"File:\n    name: {name}\n    mime_type: {mime_type}\n")


for content in gais_contents:
    if role := content.get("role", None):
        print("Role:", role, "\n")

    for n, part in enumerate(content["parts"]):
        if text := part.get("text", None):
            print(text, "\n")

        elif file_data := part.get("file_data", None):
            show_file(file_data)

    print("-" * 80, "\n")
