from urllib.parse import urlparse

def classify_urls(urls : list[str]) -> dict:

  result = {
      'github' : None,
      'linkedin': None,
      'portfolio': []
  }

  for url in urls:

    normalized_url = url if url.startswith('http') else f'https://{url}'
    domain = urlparse(normalized_url).netloc.lower().replace("www.","")

    if "github.com" in domain:
      result["github"] = normalized_url
    elif "linkedin.com" in domain:
      result["linkedin"] = normalized_url
    elif domain and '@' not in normalized_url:
      result["portfolio"].append(normalized_url)

  return result