# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


FORME_JURIDIQUE = [
							('sa',"SA"),
							('sarl',"SARL"),
							('suarl',"SUARL"),
							('ei',"EI"),
							('sci',"SCI"),
							('gie',"GIE"),
							('sas',"SAS"),
							('association',"Association"),
							('cooperative',"Coopérative"),
							('tpe',"TPE"),
							('autre',"AUTRE"),
				  ]

SITUATION_MATRIMONIALE = [
							('marie','Marié(e)'),
							('divorce','Divorcé(e)'),
							('veuf','Veuf(ve)'),
							('celibataire','Célibataire'),
						 ]

SEXE = [
		
			('masculin','Masculin'),
			('feminin','Féminin'),
		]

TRANCHE_AGE = [
				('0_20',"0 - 20 ans"),
				('20_40',"20 - 40 ans"),
				('plus_40',"plus de 40 ans"),
			   ]


class Respartner(models.Model):
	_inherit = 'res.partner'

	"""activity_sector_id = fields.Many2one('activity.sector',string = "Secteur d'activité")
	filiere_id = fields.Many2one('filiere',string = "Filière")
	type_entreprise_id = fields.Many2one('type.entreprise',string = "Type d'entreprise")
	forme_juridique_id = fields.Many2one('forme.juridique', string = "Forme juridique")
	ninea = fields.Char(string = "Ninéa")
	registre_commerce = fields.Char(string = "Registre de commerce")
	date_creation = fields.Date(string = "Date de création")
	nombre_employes = fields.Integer(string = "Nombre d'employés à ce jour ")
	capital = fields.Float(string="Capital",digits=(12,0))
	num_cni = fields.Char(string="Numéro d'identification nationale")
	sexe = fields.Selection(SEXE,"Sexe")
	dirige_par = fields.Selection([('Homme','Homme'),('Femme','Femme')],default="Homme",string="Dirigé par")
	date_naissance = fields.Date(string="Date de naissance")
	nationalite = fields.Char(string="Nationalité")
	lieu_naissance = fields.Char(string="Lieu de naissance")
	first_name = fields.Char(string='Prénom(s)')
	last_name = fields.Char(string='Nom')
	tranche_age = fields.Selection(TRANCHE_AGE,"Tranche d'age")"""
	dossier_count = fields.Integer(string="Nombre de dossiers" , compute="_compute_count_dossiers")


	def _compute_count_dossiers(self):
		dossiers = self.env['fongip.project']
		for record in self:
			record.dossier_count = dossiers.search_count([('entreprise_id','=',record.id)])


	def return_action_to_open(self):
		"""This opens the xml view specified in xml_id for the current credit garantie  """
		self.ensure_one()
		xml_id = self.env.context.get('xml_id')
		if xml_id:
			res = self.env['ir.actions.act_window'].for_xml_id('fongip_garantie',xml_id)
			res.update(
						context=dict(self.env.context,default_entreprise_id=self.id, group_by=False),
						domain=[('entreprise_id','=',self.id)]
					)
			return res
		return False


"""class PSP(models.Model):
	_name = 'fongip.psp'
	_description = 'Pole sectoriel prioritaire'

	name = fields.Char(string = "Numéro PSP")

	_sql_constraints = [('name_uniq', 'unique (name)', "Ce PSP existe déjà !")]

class ActivitySector(models.Model):
	_name = 'activity.sector'
	_description = "Secteur d'activité"

	name = fields.Char(string = "Libellé")
	psp_id = fields.Many2one('fongip.psp')

class Filiere(models.Model):
	_name = 'filiere'
	_description = 'Filière'

	name = fields.Char(string = "Nom")
	activity_sector_id = fields.Many2one('activity.sector',string = "Secteur d'activité")

class FormeJuridique(models.Model):
	_name = 'forme.juridique'
	_description = 'Forme juridique'

	name = fields.Char(string = "Abréviation")
	description = fields.Char(string = "Description")

	_sql_constraints = [('name_uniq', 'unique (name)', "Cette forme juridique existe déjà !")]

class TypeEntreprise(models.Model):
	_name = 'type.entreprise'
	_description = "Type d'entreprise"

	name = fields.Char(string = "abréviation")
	description = fields.Char(string = "Description")"""

	

"""class FongipPromoteur(models.Model):
	_name = 'fongip.promoteur'
	#_inherit = 'res.partner'
	project_id = fields.Many2one('fongip.project' , string=u'Projet' , ondelete='cascade')
	promoteur_id = fields.Many2one('res.partner' ,string='Promoteurs' , ondelete='cascade')
	first_name = fields.Char(string=u'Prénom')
	last_name = fields.Char(string=u'Nom')
	date_naissance = fields.Date(string=u'Date de naissance')
	age = fields.Integer(string=u'Age' , size=2)
	num_cni = fields.Char(string=u"Numéro d'identification" , size=128)
	defaillance = fields.Selection(DEFAILLANCE , 'Défaillance')
	date_defaillance = fields.Date(string=u'Date de la dernière défaillance')
	Situation_matrimoniale = fields.Selection(SITUATION_MATRIMONIALE , 'Situation matrimoniale')




class FongipDirigeant(models.Model):
	_name = 'fongip.dirigeant'
	#_inherit = 'fongip.promoteur'
	project_id = fields.Many2one('fongip.project' , string=u'projet' , ondelete='cascade')
	dirigeant_id = fields.Many2one('res.partner' ,string='Dirigeants' , ondelete='cascade')"""
