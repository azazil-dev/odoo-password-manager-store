# -*- coding: utf-8 -*-

from odoo import fields, models


class PasswordStoreTag(models.Model):
    _name = 'password.store.tag'
    _description = 'Password Store Tag'
    _order = 'name'

    name = fields.Char(string='Tag', required=True, translate=True)
    color = fields.Integer(string='Color Index')
