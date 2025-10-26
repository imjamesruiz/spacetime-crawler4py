import pickle

class MockResponse:
    def __init__(self, url, content):
        self.url = url
        self.content = content

class Response(object):
    def __init__(self, resp_dict):
        self.url = resp_dict["url"]
        self.status = resp_dict["status"]
        self.error = resp_dict["error"] if "error" in resp_dict else None
        
        # Handle direct download case
        if "content" in resp_dict and resp_dict["content"] is not None:
            self.raw_response = MockResponse(self.url, resp_dict["content"])
        else:
            try:
                self.raw_response = (
                    pickle.loads(resp_dict["response"])
                    if "response" in resp_dict else
                    None)
            except TypeError:
                self.raw_response = None
