# Product caching

Render would take 4 seconds to serve ```products-with-icon-image``` endpoint

So I used ```method_cache```

But then whenever I created or updated product that wasn't getting reflected even though I implemented signal to ```cache.clear()```

I found reason in [stack overflow](https://stackoverflow.com/questions/55579867/django-cache-clear-not-working-locmemcache-aws) 

```text
The problem is in the response headers. The cache_page decorator automatically adds a max-age option to the Cache-Control header in the response. So the cache clear was working properly, clearing the local memory on the server, but the user's browser was instructed not to ask the server for updated data for the duration of the timeout. And my browser was happily complying (even after Ctrl-F5).

Fortunately, there are other decorators you can use to deal with this without much difficulty, now that it's clear what's happening. Django provides a number of other decorators, such as cache_control or never_cache.

I ended up using never_cache, which turned the urls files into...
```

But the solution suggested by the stack overflow wouldn't suit me as it turned out server side caching didn't make much difference.
The fetching itself was bottleneck
So I instead used ```cache_control``` suggested by Gemini

```python
from django.views.decorators.cache import cache_page, cache_control
urlpatterns=[path("v1/products-with-icon-image/",cache_control(no_cache=True)(cache_page(60*15)(ProductWithIconImageListView.as_view())),name="products-with-icon-image"),]
```

This solution worked. Now I had products cached at browser side and whenever I created new product or updated product it would clear browser cache, because browser cache and server cache don't match anymore, as server cache was cleared, and browser would refetch products and reset cache.