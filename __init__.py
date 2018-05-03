# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import template

def register():
    Pool.register(
        template.Template,
        template.RecomputePriceStart,
        module='product_recompute_price', type_='model')
    Pool.register(
        template.RecomputePrice,
        module='product_recompute_price', type_='wizard')
