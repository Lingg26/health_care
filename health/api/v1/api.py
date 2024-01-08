# Initialize the main API router
from fastapi import APIRouter
from health.api.v1 import auth, account, category, news, product, orders, chat_with_admin, statistics, cart


def include_router(api_router: APIRouter, module, tag, prefix):
    """
    Include a router module into the main API router with the specified tag and prefix.
    """
    api_router.include_router(module.router, tags=[tag], prefix=f'/{prefix}')


main_api_router = APIRouter()


router_modules = [
    {'module': auth, 'tag': 'Auth', 'prefix': 'oauth'},
    {'module': account, 'tag': 'Account', 'prefix': 'account'},
    {'module': category, 'tag': 'Category', 'prefix': 'category'},
    {'module': news, 'tag': 'News', 'prefix': 'news'},
    {'module': product, 'tag': 'Product', 'prefix': 'product'},
    {'module': cart, 'tag': 'Cart', 'prefix': 'cart'},
    {'module': orders, 'tag': 'Order', 'prefix': 'orders'},
    {'module': chat_with_admin, 'tag': 'Chat with admin', 'prefix': 'chat_with_admin'},
    {'module': statistics, 'tag': 'Statistics', 'prefix': 'statistics'}
]

# Include the router modules dynamically
for router_module in router_modules:
    include_router(main_api_router, **router_module)