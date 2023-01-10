from flask_caching import Cache

def create_cache(config) -> Cache:
    return Cache(config=config)

cache = create_cache({'CACHE_TYPE': 'SimpleCache'})
