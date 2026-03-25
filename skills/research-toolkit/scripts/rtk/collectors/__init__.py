from rtk.collectors.manual import collect_manual
from rtk.collectors.pricing import collect_pricing
from rtk.collectors.reviews import collect_reviews
from rtk.collectors.seo import collect_seo
from rtk.collectors.social import collect_social
from rtk.collectors.web import collect_web

COLLECTOR_MAP = {
    "web": collect_web,
    "reviews": collect_reviews,
    "social": collect_social,
    "seo": collect_seo,
    "pricing": collect_pricing,
    "manual": collect_manual,
}
