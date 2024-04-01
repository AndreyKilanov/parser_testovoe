import json

from scrapy.http import HtmlResponse


def get_fs_body(url, method="get"):
    """
    A function that generates a post body dictionary for a given URL and method.
    Return post body dictionary for flare solver.
    """
    post_body = {
        "cmd": f"request.{method}",
        "url": url,
        "maxTimeout": 60000
    }
    return json.dumps(post_body)


def parse_fs_response(response):
    """
    Return response from flare solver, extracting cookies, response and user
    agent.
    """
    response = json.loads(response.text)
    cookies = response['solution']['cookies']
    user_agent = response['solution']['userAgent']
    cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    response = HtmlResponse(
        url=response['solution']['url'],
        body=response['solution']['response'],
        encoding='utf-8'
    )
    return response, cookies, user_agent


def generate_url_list(base_url, num_pages):
    """
    Generate a list of URLs based on the base URL and the number of pages.
    """
    url_list = [base_url]
    for i in range(2, num_pages + 1):
        page_url = f"{base_url}?page={i}"
        url_list.append(page_url)
    return url_list
