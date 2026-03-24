from spca.collectors.manual import collect_manual
from spca.collectors.pricing import collect_pricing
from spca.collectors.reviews import collect_reviews
from spca.collectors.seo import collect_seo
from spca.collectors.social import collect_social
from spca.collectors.web import collect_web

COLLECTOR_MAP = {
    "web": collect_web,
    "reviews": collect_reviews,
    "social": collect_social,
    "seo": collect_seo,
    "pricing": collect_pricing,
    "manual": collect_manual,
}
