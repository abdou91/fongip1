# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class SousFonds(models.Model):
	_name = 'fongip.sous_fonds'
	_description = 'Sous-fonds'

	name = fields.Char(string = "Nom")
	code = fields.Integer(string = "Code")
	description = fields.Text(string = "Description")
	managed_by = fields.Many2one('hr.employee',string = "Responsable")

	programme_ids = fields.One2many('fongip.programme','sous_fonds_id',string = "Programmes")


class Programme(models.Model):
	_name = 'fongip.programme'
	_description = 'Programme'

	name = fields.Char(string = "Libellé")
	sous_fonds_id = fields.Many2one('fongip.sous_fonds',string = "Sous fonds")
	managed_by = fields.Many2one('hr.employee',string = "Géré par")
	amount = fields.Monetary(string = "Montant")
	frais_gestion = fields.Float(string = "Frais de gestion")
	reference_convention = fields.Char(string = "Référence de la convention")
	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)

	#partner_ids = fields.One2many()
	#attachment_ids = fields.Many2many('ir.attachment',string = "Joindre la convention")