import requests
import cbor
import time

from utils.response import Response

def download(url, config, logger=None):
    if config.cache_server is None:
        # Direct download without cache server
        if logger:
            logger.warning("No cache server available, downloading directly")
        try:
            resp = requests.get(url, timeout=10)
            return Response({
                "url": url,
                "content": resp.content,
                "status": resp.status_code,
                "error": None if resp.status_code == 200 else f"HTTP {resp.status_code}"
            })
        except Exception as e:
            if logger:
                logger.error(f"Direct download error for {url}: {e}")
            return Response({
                "error": f"Direct download error: {e}",
                "status": 0,
                "url": url
            })
    
    host, port = config.cache_server
    resp = requests.get(
        f"http://{host}:{port}/",
        params=[("q", f"{url}"), ("u", f"{config.user_agent}")])
    try:
        if resp and resp.content:
            return Response(cbor.loads(resp.content))
    except (EOFError, ValueError) as e:
        pass
    logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})
