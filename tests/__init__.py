# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.product_recompute_price.tests.test_product_recompute_price import suite
except ImportError:
    from .test_product_recompute_price import suite

__all__ = ['suite']
