# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date,timedelta
import logging
import pytz
try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from io import BytesIO
class AccountMove(models.Model):
    _inherit = "account.move"

    def generate_qr(self):
        if qrcode and base64:
            if self.fel_firma:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                if self.partner_id.vat:
                    nit_emisor = self.partner_id.vat
                else:
                    nit_emisor = 'CF'
                if self.fel_url:
                    qr.add_data(self.fel_url)
                else:
                    qr.add_data('https://felpub.c.sat.gob.gt/verificador-web/publico/vistas/verificacionDte.jsf?tipo=autorizacion&numero={}&emisor={}&receptor={}&monto={}'.format(self.fel_firma,self.company_id.vat.replace('-',''),nit_emisor.replace('-',''),self.amount_total))
                qr.make(fit=True)

                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                return qr_image
            else:
                return False
        else:
            return False