# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    origen_id = fields.Integer(string='Origen ID', help='Origen ID del otro Odoo')
    origen_parent_id = fields.Integer(string='Origen Parent ID', help='Origen Parent ID del otro Odoo')

class CrmTeam(models.Model):
    _inherit = "crm.team"
    
    origen_id = fields.Integer(string='Origen ID', help='Origen ID del otro Odoo')
    

class CrmStage(models.Model):
    _inherit = "crm.stage"
    
    origen_id = fields.Integer(string='Origen ID', help='Origen ID del otro Odoo')

class CrmLead(models.Model):
    _inherit = "crm.lead"
    
    origen_id = fields.Integer(string='Origen ID', help='Origen ID del otro Odoo')

class MailMessage(models.Model):
    _inherit = "mail.message"
    
    origen_id = fields.Integer(string='Origen ID', help='Origen ID del otro Odoo')

class MailMessageSubtype(models.Model):
    _inherit = "mail.message.subtype"
    
    origen_id = fields.Integer(string='Origen ID', help='Origen ID del otro Odoo')

class IrAttachment(models.Model):
    _inherit = "ir.attachment"
    
    origen_id = fields.Integer(string='Origen ID', help='Origen ID del otro Odoo')

class IrAttachment(models.Model):
    _inherit = "mail.activity.type"
    
    origen_id = fields.Integer(string='Origen ID', help='Origen ID del otro Odoo')

class IrAttachment(models.Model):
    _inherit = "mail.activity"
    
    origen_id = fields.Integer(string='Origen ID', help='Origen ID del otro Odoo')
    
