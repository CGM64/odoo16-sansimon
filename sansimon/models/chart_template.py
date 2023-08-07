# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.addons.account.models.account_tax import TYPE_TAX_USE

import logging

_logger = logging.getLogger(__name__)

class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"

    def actualizarPlantillaID(self):
        self._cr.execute('update res_company set chart_template_id = null')
        return True
