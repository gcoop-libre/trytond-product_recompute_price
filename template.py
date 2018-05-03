# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal, ROUND_HALF_UP

from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.wizard import Button, StateTransition, StateView, Wizard
from trytond.modules.product.product import price_digits

__all__ = ['Template', 'RecomputePriceStart', 'RecomputePrice']


class Template:
    __name__ = 'product.template'
    __metaclass__ = PoolMeta

    @classmethod
    def _recompute_price_by_factor(cls, template, factor):
        new_list_price = (template.list_price * factor).quantize(
            Decimal('1.'), rounding=ROUND_HALF_UP)
        values = {
            'list_price': new_list_price,
            }
        return values

    @classmethod
    def _recompute_price_by_fixed(cls, template, factor):
        new_list_price = (template.list_price + factor).quantize(
            Decimal(str(10 ** -price_digits[1])))
        values = {
            'list_price': new_list_price,
            }
        return values

    @classmethod
    def recompute_price_by_percentage(cls, templates, percentage):
        to_write = []
        factor = Decimal(1) + Decimal(percentage)
        for template in templates:
            new_values = cls._recompute_price_by_factor(template, factor)
            if new_values:
                to_write.extend(([template], new_values))
        if to_write:
            cls.write(*to_write)

    @classmethod
    def recompute_price_by_fixed_amount(cls, templates, list_price):
        pool = Pool()
        Template = pool.get('product.template')
        to_write = []
        for template in templates:
            new_values = cls._recompute_price_by_fixed(template, list_price)
            if new_values:
                to_write.extend(([template], new_values))
        if to_write:
            Template.write(*to_write)


class RecomputePriceStart(ModelView):
    'Recompute Price - Start'
    __name__ = 'product.recompute_price.start'

    method = fields.Selection([
            ('percentage', 'By Percentage'),
            ('fixed_amount', 'Fixed Amount'),
            ], 'Recompute Method', required=True)
    percentage = fields.Float('Percentage', digits=(16, 4),
        states={
            'invisible': Eval('method') != 'percentage',
            'required': Eval('method') == 'percentage',
            },
        depends=['method'])
    list_price = fields.Numeric('List Price', digits=price_digits,
        states={
            'invisible': Eval('method') != 'fixed_amount',
            'required': Eval('method') == 'fixed_amount',
            },
        depends=['method'])


class RecomputePrice(Wizard):
    'Recompute Product List Price'
    __name__ = 'product.recompute_price'

    start = StateView('product.recompute_price.start',
        'product_recompute_price.recompute_price_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Recompute', 'compute', 'tryton-ok', default=True),
            ])
    compute = StateTransition()

    def get_additional_args(self):
        method_name = 'get_additional_args_%s' % self.start.method
        if not hasattr(self, method_name):
            return {}
        return getattr(self, method_name)()

    def get_additional_args_percentage(self):
        return {
            'percentage': self.start.percentage,
            }

    def get_additional_args_fixed_amount(self):
        return {
            'list_price': self.start.list_price,
            }

    def transition_compute(self):
        pool = Pool()
        Template = pool.get('product.template')

        method_name = 'recompute_price_by_%s' % self.start.method
        method = getattr(Template, method_name)
        if method:
            method(Template.browse(Transaction().context.get('active_ids')),
                **self.get_additional_args())
        return 'end'
