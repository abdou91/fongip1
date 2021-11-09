# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


#----------------------------------Commission de garantie-------------------------

class fongipFacture(models.Model):
	_name = 'fongip.commission'
	_description = 'Commission'

	commission_line_ids = fields.One2many('fongip.commission_line','commission_id',string="Tableau amortissements")
	credit_garantie_id = fields.Many2one('fongip.credit' , string='credit' , ondelete='cascade')
	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	commission_ht = fields.Monetary(string = "Commission de garantie HT",compute='_compute_commission')#,compute='_compute_commission'
	commission_ttc = fields.Monetary(string = "Commission de garantie TTC",compute='_compute_commission')


	@api.depends('commission_line_ids.commission_ttc','commission_line_ids.commission_ht')
	def _compute_commission(self):
		for record in self:
			record.commission_ht = sum(record.commission_line_ids.mapped('commission_ht'))
			record.commission_ttc = sum(record.commission_line_ids.mapped('commission_ttc'))



class fongipFactureLine(models.Model):
	_name = 'fongip.commission_line'
	_description = 'Commission Line'
	#decaissement_id = fields.Many2one('fongip.decaissement',string="Décaissement")
	commission_id = fields.Many2one('fongip.commission',string = "Facture commission",ondelete='cascade')
	periode = fields.Char(string = "Période")
	capital_debut_periode = fields.Float(string = "Capital en début de période",digits=(10,0))
	capital_rembourse = fields.Float(string = "Capital remboursé",digits=(10,0))
	interet = fields.Float(string = "Intérêt",digits=(10,0))
	capital_fin_periode = fields.Float(string = "Capital en fin de période",digits=(10,0))
	commission_ht = fields.Float(string = "Commission de garantie (HT)",digits=(10,0))
	commission_ttc = fields.Float(string = "Commission de garantie (TTC)",digits=(10,0))
