# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


TYPE_GARANTIE = [
					('individuelle',"Garantie Individuelle"),
				 	('portefeuille',"Garantie Portefeuille"),
				]

TYPE_PROJET = [
					('creation',"Création"),
			   		('extension',"Extension"),
			  ]
TYPE_PRODUIT = [
					('investissement_creation',"Investissement création"),
					('investissement_extension',"Investissement extension"),
					('exploitation',"Exploitation"),
			   ]

STATES = [
			('draft',"Brouillon"),
			('submitted',"Soumis"),
			('validated',"Validé"),
			('precomite',"Précomité"),
			('cei',"CEI"),
			('cgb',"CGB"),
			('octroye',"Octroyé"),
			('refuse',"Refusé"),
			#('rejected',"Rejeté"),
			
			#('caduque',"Caduque commission"),
			#('unpaid',"Impayé"),
			#('litigieux',"Litigieux"),
			#('solde',"Soldé"),
			#('engaged',"Engagé"),
			
			
		 ]

TYPE_IMMOBILISATION = [
						('corporelle','Corporelle'),
						('incorporelle','Incorporelle'),
					  ]
DEFAILLANCE = [
					('jamais','Jamais'),
					('au_moins_une_fois' , 'Au moins une fois'),
					('defaillance' , 'Défaillance'),
			  ]

TRANCHE_AGE = [
				('0_20',"0 - 20 ans"),
				('20_40',"20 - 40 ans"),
				('plus_40',"plus de 40 ans"),
			   ]


RESTRUCTURATION = [
					('restructure',"Restructuré"),
					('non_restructure',"Non restructuré"),
					("archive","Archivé") ,
				  ]



class FongipReseau(models.Model):
	_name = 'fongip.reseau'
	_description = 'Réseau'
	name = fields.Char(string=u'Nom')


class FongipProject(models.Model):
	_name = 'fongip.project'
	_description = 'projet'

	name = fields.Char(string=u'Intitulé du projet' , required=True)
	#------------------------Imputation---------------
	#imputation_id = fields.Many2one('fongip.imputation',string="Imputation")
	#analyste = fields.Many2one('res.users',string="Analyste")
	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	type_garantie = fields.Selection(TYPE_GARANTIE,string = 'Type de garantie')
	project_type = fields.Selection(TYPE_PROJET,string = "Situation de l'entreprise")
	banque_id = fields.Many2one('res.bank',string='Banque' , ondelete='cascade')
	entreprise_id = fields.Many2one('res.partner',string=u'entreprise' , ondelete = 'cascade')
	type_produit = fields.Selection(TYPE_PRODUIT , "Type de produit")
	state = fields.Selection(STATES , 'Statut du dossier' , default="draft",readonly = True)
	montant_total_credit = fields.Monetary(string=u'Montant total du crédit' ,compute='_compute_montant_total_credit' , store=True)
	montant_total_garantie = fields.Monetary(string=u'Montant total de la garantie' , compute='_compute_montant_total_garantie' ,store=True)
	montant_financement = fields.Monetary(string=u'Montant du financement')
	nombre_emplois_a_creer = fields.Float(string=u"à créer" )
	nombre_emplois_a_consolider = fields.Float(string=u"à consolider")
	numero = fields.Integer(string=u'Numéro')
	numero_dossier = fields.Char(string=u'Numéro du dossier' , size=128 )
	credit_ids = fields.One2many('fongip.credit','project_id', 'Crédits')
	immobilisation_ids = fields.One2many('fongip.immobilisation', 'project_id' , 'Immobilisations')
	bfr_ids = fields.One2many('fongip.bfr','project_id','BFR')
	divers_ids = fields.One2many('fongip.divers','project_id','Divers')
	apport_ids = fields.One2many('fongip.apport','project_id','Apport')
	emprunt_ids = fields.One2many('fongip.emprunt','project_id','Emprunt')
	surety_ids = fields.One2many('fongip.surety','project_id','suretés')
	produits = fields.Char(string=u'Produits')
	#activity_sector_id = fields.Many2one('fongip.secteur_activite' , string=u"Secteur d'activités")
	#psp_num = fields.Char(related='activity_sector_id.psp_id.name',string='PSP',store=True)
	#filiere_id = fields.Many2one('fongip.filiere' , string=u'Filière')
	reseau_id = fields.Many2one('fongip.reseau',string=u'Réseau')
	numero_dossier_banque = fields.Char(string=u'Numéro de dossier de banque')
	locality = fields.Char(string = "Localisation du projet")
	date_debut_saisie = fields.Date(string=u'Date debut de saisie' , default=fields.Date.context_today)
	date_soumission = fields.Date(string=u'Date de soumission')
	date_validation = fields.Date(string=u'Date de validation')
	date_precomite = fields.Date(string=u'Date de précomité')
	date_cei = fields.Date(string=u'Date CEI')
	date_cgb = fields.Date(string=u'Date de CGB')
	date_octroi_garantie = fields.Date(string=u"Date d'octroi de la garantie")
	date_refus_garantie = fields.Date(string=u'Date refus de garantie')
	date_de_transmission = fields.Date(string=u"Date de transmission")
	total_programme_investissement = fields.Monetary(string=u"Total programme d'invesstissement" , compute='_compute_total_programme_investissement', store=True)
	total_plan_financement = fields.Monetary(string=u"Total programme financement" , compute='_compute_total_plan_financement' , store=True)
	total_immobilisations = fields.Monetary(string=u'Total Immobilisations' , compute='_compute_montant_total_immobilisation',store=True)
	total_immobilisations_corporelles = fields.Monetary(string=u"Total immobilisations corporelles" ,compute='_compute_montant_total_immobilisation',store=True)
	total_immobilisations_incorporelles = fields.Monetary(string=u"Total immobilisation incorporelles" , compute='_compute_montant_total_immobilisation',store=True)
	total_bfr = fields.Monetary(string=u'Total BFR' ,compute='_compute_montant_total_bfr',store=True )
	total_divers = fields.Monetary(string=u'Total divers' , compute='_compute_montant_total_divers', store=True)
	total_apport = fields.Monetary(string=u'Total apport' , compute='_compute_montant_total_apport',store=True)
	total_emprunt = fields.Monetary(string=u'Total emprunt' , compute='_compute_montant_total_emprunt',store=True)
	total_suretes = fields.Monetary(string=u'Total suretés' ,compute='_compute_total_surety' , store=True)
	poids_immobilisations = fields.Float(string=u'Poids immo' , digits=(2,2) , compute='_compute_total_programme_investissement',store=True)
	poids_bfr = fields.Float(string=u'Poids BFR' , digits=(2,2) ,compute='_compute_total_programme_investissement', store=True)
	poids_divers = fields.Float(string=u'Poids DIVERS' , digits=(2,2) , compute='_compute_total_programme_investissement',store=True)
	poids_apport = fields.Float(string=u'Poids APPORT', digits=(2,2) , compute='_compute_total_plan_financement',store=True)
	poids_emprunt = fields.Float(string=u'Poids EMPRUNT', digits=(2,2) , compute='_compute_total_plan_financement',store=True)
	numero_dossier = fields.Char(string=u'Numéro dossier FONGIP')
	#pays_id = fields.Many2one('fongip.pays' , string='Pays')
	region_id = fields.Many2one('res.country.region' , string = 'Région' , ondelete = 'cascade')
	departement_id = fields.Many2one('res.country.department' , string = 'Département' , ondelete = 'cascade')
	number_of_jobs = fields.Integer(string=u"Nombre d'emplois crées")
	number_of_direct_jobs = fields.Integer(string="Nombre d'emplois directs crées")
	number_of_indirect_jobs = fields.Integer(string="Nombre d'emplois indirectement crées")
	action = fields.Selection(RESTRUCTURATION , 'Restructuration',default='non_restructure')
	date_restructuration = fields.Date(string='Date de restructuration')
	credit_count = fields.Integer(string="Nombre de crédits" , compute="_compute_count_credits")
	#promoteur_ids = fields.One2many('fongip.promoteur','project_id',string='Promoteur(s)')
	#dirigeant_ids = fields.One2many('fongip.dirigeant','project_id',string='Dirigeant(s)')

	"""@api.model
	def create(self,data):
		if 'imputation_id' in data and data['imputation_id']:
			self.env['fongip.imputation'].browse(data['imputation_id']).write({'state':'en_cours','etat':"En cours d'instruction"})
		#project = super(FongipProject, self.with_context(mail_create_nolog=True)).create(data)
		#project.message_post(body=_('dossier %s de %s  crée avec succès!') % (project.name,project.entreprise_id.name))
		return project"""

	def generer_numero_dossier(self):
		if self.banque_id and self.date_cgb:
			code_banque = self.banque_id.code_banque	
			dossier_count = self.env['fongip.project'].search_count([('banque_id','=',self.banque_id.id),('action','!=','archive')])
			number = 1
			annee_cgb = self.date_cgb.split("-")[0][2:]
			moi_cgb = self.date_cgb.split("-")[1]
			if dossier_count:
				number = dossier_count
			numero = str(number)
			if len(numero) == 1:
				numero = "000"+numero
			if len(numero) == 2:
				numero = "00"+numero
			if len(numero) == 3:
				numero = "0"+numero
			numero_dossier = annee_cgb+'-'+moi_cgb+'-'+code_banque+'-'+numero
			#print numero_dossier
			return self.write({'numero':number,'numero_dossier':numero_dossier})
	
	def restructurer(self):
		assert len(self.ids) == 1 , "This operation should only be done for 1 single dossier at a time, as it suppose to open a window as result"
		for dossier in self:
			dossier.action = 'restructure'
			#credit_archives =  []
			for credit in dossier.credit_ids:
				credit.write({'action':'restructure'})
			default = {
						'date_restructuration':fields.Date.context_today(self),
						'action':'archive'
					}
			new_id = dossier.copy(default).id
			#Archiver les lignes de credits aussi
			for credit in dossier.credit_ids:
				credit.copy({'action':'archive','project_id':new_id})
		return {
					'name' : _("Restructuration"),
					'view_mode' : 'form',
					'view_id' : self.env.ref('fongip_garantie.fongip_project_view_form').id,
					'view_type' : 'tree,form',
					'res_model' : 'fongip.project',
					'type' : 'ir.actions.act_window',
					'domain' : '[]',
					'res_id' : new_id,
					'context' : {'active_id' : new_id},
				}

	def open_project_before_restructured(self):
		self.ensure_one()
		dossier = self.search([('action','=','archive'),('name','like',self.name)],limit = 1)
		xml_id = self.env.context.get('xml_id')
		if xml_id:
			res = self.env['ir.actions.act_window']._for_xml_id('fongip_garantie.%s' % xml_id)
			res.update(
						context=dict(self.env.context,active_id=dossier.id, group_by=False),
						domain=[('id','=',dossier.id)]
					)
			return res
		return False


	@api.depends('credit_ids.montant_garantie')
	def _compute_montant_total_garantie(self):
		for project in self:
			project.montant_total_garantie = sum(project.credit_ids.mapped('montant_garantie'))

	@api.depends('credit_ids.montant')
	def _compute_montant_total_credit(self):
		for project in self:
			project.montant_total_credit = sum(project.credit_ids.mapped('montant'))
	
	@api.depends('immobilisation_ids.value')
	def _compute_montant_total_immobilisation(self):
		for project in self:
			project.total_immobilisations = sum(project.immobilisation_ids.mapped('value'))
			project.total_immobilisations_corporelles = sum(project.immobilisation_ids.mapped(lambda r: r.value if r.type_immobilisation=='corporelle' else 0))
			project.total_immobilisations_incorporelles = sum(project.immobilisation_ids.mapped(lambda r: r.value if r.type_immobilisation=='incorporelle' else 0))

	@api.depends('bfr_ids.value')
	def _compute_montant_total_bfr(self):
		for project in self:
			project.total_bfr = sum(project.bfr_ids.mapped('value'))

	@api.depends('divers_ids.value')
	def _compute_montant_total_divers(self):
		for project in self:
			project.total_divers = sum(project.divers_ids.mapped('value'))

	@api.depends('apport_ids.value')
	def _compute_montant_total_apport(self):
		for project in self:
			project.total_apport = sum(project.apport_ids.mapped('value'))

	@api.depends('emprunt_ids.value')
	def _compute_montant_total_emprunt(self):
		for project in self:
			project.total_emprunt = sum(project.emprunt_ids.mapped('value'))

	@api.depends('surety_ids.value')
	def _compute_total_surety(self):
		for project in self:
			project.total_suretes = sum(project.surety_ids.mapped('value'))

	@api.depends('total_immobilisations','total_bfr' ,'total_divers')
	def _compute_total_programme_investissement(self):
		for project in self:
			project.total_programme_investissement = project.total_immobilisations + project.total_bfr + project.total_divers
			if project.total_programme_investissement > 0:
				project.poids_immobilisations = round((project.total_immobilisations * 100.00) / (project.total_immobilisations + project.total_bfr + project.total_divers),2)
				project.poids_bfr = round((project.total_bfr * 100.00) / (project.total_immobilisations + project.total_bfr + project.total_divers),2)
				project.poids_divers = round((project.total_divers * 100.00) / (project.total_immobilisations + project.total_bfr + project.total_divers),2)

	@api.depends('total_apport','total_emprunt')
	def _compute_total_plan_financement(self):
		for project in self:
			project.total_plan_financement = project.total_apport + project.total_emprunt
			if project.total_plan_financement > 0:
				project.montant_financement = project.total_apport + project.total_emprunt
				project.poids_apport = round((project.total_apport * 100.00) / (project.total_apport + project.total_emprunt),2)
				project.poids_emprunt = round((project.total_emprunt * 100.00) / (project.total_apport + project.total_emprunt),2)


	def _compute_count_credits(self):
		credits = self.env['fongip.credit']
		for record in self:
			record.credit_count = credits.search_count([('project_id','=',record.id)])


	"""@api.onchange('emprunt_ids')
	def onchange_emprunt(self):
		if self.emprunt_ids:
			for emprunt in self.emprunt_ids:"""


	def soumettre(self):
		#verifier si tous les champs obligatoires ont ete rempli
		for record in self:
			record.state='submitted'
			record.date_soumission = fields.Date.context_today(self)
			if not record.entreprise_id:
				raise UserError(_(u"Le champs entreprise doit etre renseigné"))
			"""if not record.activity_sector_id:
				raise UserError(_(u"Le champs secteur d'activité doit etre renseigné"))
			if not record.filiere_id:
				raise UserError(_(u"Le champs filière doit etre renseigné"))"""
			if not record.produits:
				raise UserError(_(u"Le champs produit doit etre renseigné"))
			if record.total_programme_investissement != record.total_plan_financement:
				raise UserError(_(u"Le total du plan de financement doit être égal au total du programme d'investissement"))

	def valider(self):
		for record in self:
			record.state = 'validated'
			record.date_validation = fields.Date.context_today(self)

	def precomiter(self):
		for record in self:
			record.state = 'precomite' 
			record.date_precomite = fields.Date.context_today(self)

	def cei(self):
		for record in self:
			record.state = 'cei'
			record.date_cei = fields.Date.context_today(self)

	def cgb(self):
		for record in self:
			record.state = 'cgb'
			record.date_cgb = fields.Date.context_today(self)

	def octroyer(self):
		for record in self:
			record.state = 'octroye'
			record.date_octroi_garantie = fields.Date.context_today(self)

	def refuser(self):
		for record in self:
			record.state = 'refuse'
			record.date_refus_garantie = fields.Date.context_today(self)

	def remettre_en_brouillon(self):
		for record in self:
			record.state = 'draft'


	def return_action_to_open(self):
		"""This opens the xml view specified in xml_id for the current credit garantie  """
		self.ensure_one()
		xml_id = self.env.context.get('xml_id')
		if xml_id:
			res = self.env['ir.actions.act_window']._for_xml_id('fongip_garantie.%s' % xml_id)
			res.update(
						context=dict(self.env.context,default_project_id=self.id, group_by=False),
						domain=[('project_id','=',self.id)]
					)
			return res
		return False

	"""@api.onchange('imputation_id')
	def onchange_imputation_id(self):
		if not self.imputation_id:
			return 
		self.name = self.imputation_id.name
		self.analyste = self.imputation_id.impute_a.id"""





class FongipApport(models.Model):
	_name = 'fongip.apport'
	_description = 'Apport'

	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	project_id = fields.Many2one('fongip.project' , string=u'Projet' , ondelete='cascade')
	label = fields.Char(string=u'Libellé')
	poids = fields.Float(string=u'Poids' , digits=(2,2) , readonly = True)
	value = fields.Float(string=u'Montant' , digits=(12,0))

class FongipEmprunt(models.Model):
	_name = 'fongip.emprunt'
	_description = 'Emprunt'

	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	project_id = fields.Many2one('fongip.project' , string=u'Projet' , ondelete='cascade')
	origine_credit = fields.Many2one('res.bank' , string=u'Origine du crédit')
	type_credit = fields.Many2one('fongip.type_credit' , string=u'Type de crédit')
	label = fields.Char(string=u'Libellé')
	poids = fields.Float(string=u'Poids' , digits=(2,2) , readonly = True)
	value = fields.Float(string=u'Montant' , digits=(12,0))

class FongipImmobilisation(models.Model):
	_name = 'fongip.immobilisation'
	_description = 'Immobilisations'

	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	project_id = fields.Many2one('fongip.project' , string=u'Projet' , ondelete='cascade')
	label = fields.Char(string=u'Libellé' , size = 256)
	value = fields.Float(string=u'Montant(XOF)' , digits = (12,0))
	type_immobilisation = fields.Selection(TYPE_IMMOBILISATION , "Type d'immobilisation")

class FongipBfr(models.Model):
	_name = 'fongip.bfr'
	_description = 'BFR'

	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	project_id = fields.Many2one('fongip.project' , string=u'Projet' , ondelete='cascade')
	label = fields.Char(string=u'Libellé' ,size=256)
	value = fields.Float(string=u'Montant(XOF)' , digits=(12,0))
class FongipDivers(models.Model):
	_name = 'fongip.divers'
	_description = 'Divers'

	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	project_id = fields.Many2one('fongip.project' , string=u'Projet',ondelete='cascade')
	label = fields.Char(string=u'Label' ,size=256)
	value = fields.Float(string=u'Montant' , digits=(12,0))


class FongipSuretyType(models.Model):
	_name = 'fongip.surety.type'
	_description = 'Type de surete'
	name = fields.Char(string=u'Nom')

class FongipSurety(models.Model):
	_name = 'fongip.surety'
	_description = 'Surete'

	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	project_id = fields.Many2one('fongip.project' , string=u'Projet' , ondelete = 'cascade')
	surety_type_id = fields.Many2one('fongip.surety.type' , string=u'Type de sureté')
	label = fields.Char(string=u'Libellé' ,size=256)
	value = fields.Float(string=u'Montant(XOF)' , digits=(12,0))
	cotation = fields.Integer(string=u'Cotation' , readonly = True)
