# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

GENRE = [
				('Homme','Homme'),
				('Femme','Femme'),
		]
class ResPartner(models.Model):
	_inherit = 'res.partner'

	legal_status_id = fields.Many2one('legal.status',string = "Forme juridique")
	activity_sector_id = fields.Many2one('activity.sector',string = "Secteur d'activité")
	filiere_id = fields.Many2one('financing.filiere',string = "Filière")
	num_cni = fields.Char(string="Numéro d'identification nationale")
	genre = fields.Selection(GENRE, string = "Genre",default = "Homme")
	date_of_birth = fields.Date(string = "Date de naissance")

	#res.partner.industry : secteur d'activite de lentreprise

class FormeJuridique(models.Model):
	_name = 'legal.status'
	_description = 'Forme juridique'

	name = fields.Char(string = "Abréviation")
	description = fields.Char(string = "Description")

	_sql_constraints = [('name_uniq', 'unique (name)', "Cette forme juridique existe déjà !")]


class PSP(models.Model):
	_name = 'financing.psp'
	_description = 'Pole sectoriel prioritaire'

	name = fields.Char(string = "Numéro PSP")

	_sql_constraints = [('name_uniq', 'unique (name)', "Ce PSP existe déjà !")]

class ActivitySector(models.Model):
	_name = 'activity.sector'
	_description = "Secteur d'activité"

	name = fields.Char(string = "Libellé")
	psp_id = fields.Many2one('financing.psp')

class Filiere(models.Model):
	_name = 'financing.filiere'
	_description = 'Filiere'

	name = fields.Char(string = "Nom")
	activity_sector_id = fields.Many2one('activity.sector',string = "Secteur d'activité")

class Region(models.Model):
	_name = 'res.country.region'
	_description = 'Region'

	name = fields.Char(string = "Nom")
	code = fields.Char(string = "code")
	country_id = fields.Many2one('res.country',string = "Pays")
	


