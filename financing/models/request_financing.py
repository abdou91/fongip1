# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from datetime import date


RECEPTION_MODE = [
						('dossier_electronique','Dossier électronique'),
						('dossier_physique','Dossier physique'),
				 ]
class FinancingRequest(models.Models):
	_name = 'financing.request'
	_description = 'Request financing'

	name = fields.Char()
	number = fields.Char(string = "Numéro")
	reception_mode = fields.Selection(
		RECEPTION_MODE,
		default="dossier_physique",
		string = "Mode de réception"
	)
	currency_id = fields.Many2one(
        'res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id
    )

    project_cost = fields.Monetary(string = "Cout du projet")
    credit_requested = fields.Monetary(string = "Crédit sollicité")
    quotite = fields.Float(string = "Quotité de garantie")
    guarantee_amount = fields.Monetary(string = "Garantie éventuelle",compute = '_compute_guarantee_amount',store=True)
    transmission_date = fields.Date(string = "Date de transmission")
    number_of_job = fields.Integer(string = "Nombre d'emplois")
    imputation_date = fields.Date(string = "Date d'imputation à l'ingénieur")
    transmitted_to = fields.Many2one('hr.employee',string = "Transmis à")
    partner_id = fields.Many2one('res.partner',string = "Porteur de projet")
    #partner_name = fields.Char(string = "")

    @api.depends('credit_requested','quotite')
    def _compute_guarantee_amount(self):
    	if self.credit_requested and self.quotite:
    		self.guarantee_amount = (self.credit_requested * quotite) // 100



