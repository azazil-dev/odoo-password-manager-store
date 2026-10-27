# -*- coding: utf-8 -*-

from odoo import fields, models


class PasswordStoreCategory(models.Model):
    _name = 'password.store.category'
    _description = 'Password Store Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True, translate=True)
    account_count = fields.Integer(
        string='Accounts',
        compute='_compute_account_count',
    )
    active = fields.Boolean(default=True)

    def _compute_account_count(self):
        data = self.env['password.store.account']._read_group(
            [('category_id', 'in', self.ids)],
            groupby=['category_id'],
            aggregates=['__count'],
        )
        counts = {cat.id: count for cat, count in data}
        for rec in self:
            rec.account_count = counts.get(rec.id, 0)
