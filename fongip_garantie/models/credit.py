# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

MISE_EN_PLACE = [
					('oui',"Oui"),
					('en_attente',"En attente"),
					('annulee',"Annulée"),
				]

TYPE_REMBOURSEMENT = [
						('1',"Mensuel"),
						('3',"Trimestriel"),
						('6',"Semestriel"),
						('12',"Annuel")
					 ]

RESTRUCTURATION = [
					('restructure',"Restructuré"),
					('non_restructure',"Non restructuré"),
					("archive","Archivé") ,
				  ]


class FongipTypeCredit(models.Model):
	_name = 'fongip.type_credit'
	_description = 'type de crédit'

	name = fields.Char(string=u'Nom')

class FongipEtatCredit(models.Model):
	_name = 'fongip.etat_credit'
	_description = 'etat du crédit'

	name = fields.Char(string=u'Libellé')


class FongipCreditGarantie(models.Model):
	_name = 'fongip.credit'
	_description = 'Crédit'
	_rec_name = 'description'

	project_id = fields.Many2one('fongip.project' , string=u'Projet' , ondelete = 'cascade')
	origine_credit = fields.Many2one('res.bank' , string=u'Banque' , ondelete = 'cascade')
	type_credit_id = fields.Many2one('fongip.type_credit' , string=u'Type de crédit')
	sous_fond_id = fields.Many2one('fongip.sous_fonds' , string=u'Sous fonds')
	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)

	montant = fields.Monetary(string=u'Montant du crédit') #, required=True 
	#montant financement
	#montant_financement = fields.Float(string=u'Montant du financement' , digits = (12,0) , size = 128)
	etat_credit_id = fields.Many2one('fongip.etat_credit' , string=u'Etat du credit' , ondelete='cascade')
	etat_credit_name = fields.Char(related='etat_credit_id.name',string='Etat du crédit' , store=True)
	#type_garantie = fields.Selection(TYPE_GARANTIE,'Type de garantie')
	duree = fields.Integer(string=u'Durée(en mois)')
	date_cgb = fields.Date(string=u'Date CGB')
	duree_differee = fields.Integer(string=u'Durée du différé (en mois)')
	amortissable = fields.Boolean(string=u'Crédit amortissable')
	visible = fields.Boolean(string=u'Invisible')
	quotite = fields.Integer(string=u'Quotite de garantie (%)' )
	date_premiere_echeance = fields.Date(string=u"Date première échéance")
	date_derniere_echeance = fields.Date(string=u"Date dernière échéance")
	taux = fields.Float(string=u"Taux d'intérêt(%)")
	taux_commission = fields.Float("Taux commission")
	montant_commission = fields.Monetary(string=u'Montant commission')
	montant_echeance = fields.Monetary(string=u"Montant de l'échéance")
	type_remboursement = fields.Selection(TYPE_REMBOURSEMENT , 'Type de remboursement')
	montant_garantie = fields.Monetary(string=u'Montant de la garantie',compute='_compute_montant_garantie' ,store=True)#, 
	mise_en_place = fields.Selection(MISE_EN_PLACE, "Mise en place")
	date_mise_en_place = fields.Date(string=u'Date de mise en place')
	encours_credit = fields.Monetary(string=u'Encours du crédit')
	encours_garantie = fields.Monetary(string=u'Encours de la garantie')
	description = fields.Text(string=u'Objet')
	nombre_echeances_impayes = fields.Integer(string=u"Nombre d'échéances impayés" , compute='compute_impayes',store=True)
	montant_impayes = fields.Monetary(string=u"Montant total des impayés", compute='compute_impayes' , store=True)
	montant_indemnisations = fields.Monetary(string=u'Montant indemnisation')
	#montant_rembourse = fields.Float(string='Montant remboursé',digits=())
	observations = fields.Text(string="Observations")
	code = fields.Float(string=u"Code")
	credit_impaye_ids = fields.One2many('fongip.credit.impaye','credit_garantie_id','les impayés')
	date_declassement = fields.Date(string="Déclassé le ")
	date_annulation = fields.Date(string='Annulé le ')
	action = fields.Selection(RESTRUCTURATION , 'Restructuration',default='non_restructure')
	amortissement_line_ids = fields.One2many('fongip.amortissement.line','credit_garantie_id',string="Tableau d'amortissement")
	#amortissable = fields.Boolean(string='Amortissable')
	differe = fields.Boolean(string='différé')
	#visible = fields.Boolean(string='Visiblité',default=False)
	#region_id = fields.Many2one('fongip.region' , string = 'Région' , ondelete = 'cascade')
	#departement_id = fields.Many2one('fongip.departement' , string = 'Département' , ondelete = 'cascade')

	@api.depends('montant','quotite')
	def _compute_montant_garantie(self):
		for record in self:
			if record.montant and record.quotite:
				record.montant_garantie = (record.montant * record.quotite) /100.0

	@api.depends('amortissement_line_ids.status')
	def compute_impayes(self):
		amortissement_lines = self.env['fongip.amortissement.line']
		for record in self:
			nombre_echeances_impayes = amortissement_lines.search_count([('credit_garantie_id','=',self.id),('status','=','impaye')])
			record.nombre_echeances_impayes = nombre_echeances_impayes
			record.montant_impayes = sum(record.amortissement_line_ids.mapped(lambda r: r.annuite if r.status =='impaye' else 0))
			if nombre_echeances_impayes > 0:
				etat_credit_id = self.env['fongip.etat_credit'].search([('name','like','Impayé')],limit=1).id
				self.write({'etat_credit_id':etat_credit_id})
			elif nombre_echeances_impayes == 0:
				etat_credit_id = self.env['fongip.etat_credit'].search([('name','like','Sain')],limit=1).id
				self.write({'etat_credit_id':etat_credit_id})

	
	@api.onchange('amortissement_line_ids.status')
	def onchange_impayes(self):
		amortissement_lines = self.env['fongip.amortissement.line']
		for record in self:
			nombre_echeances_impayes = amortissement_lines.search_count([('credit_garantie_id','=',self.id),('status','=','impaye')])
			record.nombre_echeances_impayes = nombre_echeances_impayes
			record.montant_impayes = sum(record.amortissement_line_ids.mapped(lambda r: r.annuite if r.status =='impaye' else 0))
			if nombre_echeances_impayes > 0:
				etat_credit_id = self.env['fongip.etat_credit'].search([('name','like','Impayé')],limit=1).id
				self.write({'etat_credit_id':etat_credit_id})
			elif nombre_echeances_impayes == 0:
				etat_credit_id = self.env['fongip.etat_credit'].search([('name','like','Sain')],limit=1).id
				self.write({'etat_credit_id':etat_credit_id})
	"""@api.depends('credit_impaye_ids.nombre_echeances')
	def _compute_nombre_echeances_impayes(self):
		for credit in self:
			credit.nombre_echeances_impayes = sum(credit.credit_impaye_ids.mapped(lambda r: r.nombre_echeances if r.state=='non_regularise' else 0))

	@api.depends('credit_impaye_ids.montant')
	def _compute_montant_impayes(self):
		for credit in self:
			credit.montant_impayes = sum(credit.credit_impaye_ids.mapped(lambda r: r.montant if r.state !='regularise' else 0))"""

	"""@api.depends('taux','type_remboursement','duree','duree_differee','montant')
	def _compute_montant_echeance(self):
		for record in self:
			if record.taux and record.type_remboursement and record.duree and record.montant:
				TauxInteretEcheance = round(record.taux / (12 * 100 * int(record.type_remboursement)),4)
				NombreEcheance = record.duree / int(record.type_remboursement)
				MontantEcheance = round(montant * TauxInteretEcheance / (1 - (1 + TauxInteretEcheance)**(-(NombreEcheance - duree_differee))),0)
				self.montant_echeance = MontantEcheance"""

	def declasser(self):
		etat_credit_id = self.env['fongip.etat_credit'].search([('name','like','Déclassé')],limit=1).id
		for record in self:
			if etat_credit_id:
				record.etat_credit_id = etat_credit_id
				record.date_declassement = fields.Date.context_today(self)

	def annuler(self):
		etat_credit_id = self.env['fongip.etat_credit'].search([('name','like','Annulé')],limit=1).id
		for record in self:
			if etat_credit_id:
				record.etat_credit_id = etat_credit_id
				record.date_annulation = fields.Date.context_today(self)


	def declarer_impaye(self):
		return ""

	def return_action_to_open(self):
		"""This opens the xml view specified in xml_id for the current credit garantie  """
		self.ensure_one()
		xml_id = self.env.context.get('xml_id')
		if xml_id:
			res = self.env['ir.actions.act_window'].for_xml_id('fongip_garantie',xml_id)
			res.update(
						context=dict(self.env.context,default_credit_garantie_id=self.id, group_by=False),
						domain=[('credit_garantie_id','=',self.id)]
					)
			return res
		return False

	def calcule_encours(self):
		
		return True

	def update_tableau_amortissement(self):
		for record in self:
			amortissement_line_ids = self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.id)])
			if amortissement_line_ids:
				for line in amortissement_line_ids:
					if record.duree_differee and line.numero <= record.duree_differee:
						pass
					else:
						if line.numero > 1:
							previous_line = self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.id),('numero','=',line.numero - 1)],limit=1)
							if previous_line:
								line.capital_debut_periode = previous_line.capital_fin_periode
						line.annuite = record.montant_echeance
						line.capital_rembourse = line.annuite - line.interet
						line.capital_fin_periode = line.capital_debut_periode - line.capital_rembourse
		"""for record in self:
			amortissement_line_ids = self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.id)])
			if amortissement_line_ids:
				for line in amortissement_line_ids:
					if line.numero > 1:
						previous_line = self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.id),('numero','=',line.numero - 1)],limit=1)
						if previous_line:
							line.capital_debut_periode = previous_line.capital_fin_periode
					line.annuite = record.montant_echeance
					line.capital_rembourse = line.annuite - line.interet
					line.capital_fin_periode = line.capital_debut_periode - line.capital_rembourse"""
					


	def generer_tableau_amortissement(self):
		for record in self:
			amortissement_line_ids = self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.id)])
			if amortissement_line_ids:
				amortissement_line_ids.unlink()
			CapitalEnDebutPeriode = record.montant
			QuotiteGarantie = record.quotite
			TauxCommissionDeGarantie = record.taux_commission
			Calendrier = fields.Date.from_string(record.date_premiere_echeance)
			NbMoisEntreEcheance = int(record.type_remboursement)
			duree_differee = record.duree_differee
			if not duree_differee:
				duree_differee = 0
			if not record.date_premiere_echeance:
				raise UserError(_(u"Merci de remplir le champs date de première échéance"))
			try:
				TauxInteretEcheance = round(record.taux / (12 * 100 * NbMoisEntreEcheance),4)
				NombreEcheance = int(record.duree / NbMoisEntreEcheance)
				MontantEcheance = round(CapitalEnDebutPeriode * TauxInteretEcheance / (1 - (1 + TauxInteretEcheance)**(-(NombreEcheance - duree_differee))),0)
			except ZeroDivisionError:
				raise UserError(_('Une erreur est survenue lors de la génération du tableau des amortissements!! Vérifiez que les chmaps mois entre chaque échéance, taux et duree sont correctement remplis'))

			somme_commission_garantie = 0
			for num in range(1,NombreEcheance +1):
				EngagementDeGarantie = CapitalEnDebutPeriode * QuotiteGarantie / 100.0
				CommissionDeGarantie = CapitalEnDebutPeriode * QuotiteGarantie * TauxCommissionDeGarantie / 10000.0
				interets = round(CapitalEnDebutPeriode * TauxInteretEcheance , 0)
				if num > duree_differee:
					CapitalRembourse = round(MontantEcheance - interets,0)
				else:
					CapitalRembourse = 0
				CapitalEnFinPeriode = round(CapitalEnDebutPeriode - CapitalRembourse)
				vals = {}
				vals['credit_garantie_id'] = record.id
				vals['echeance'] = fields.Date.to_string(Calendrier)
				vals['numero'] = num
				vals['capital_rembourse'] = CapitalRembourse
				vals['capital_debut_periode'] = CapitalEnDebutPeriode
				vals['capital_fin_periode'] = CapitalEnFinPeriode
				vals['interet'] = interets
				if CapitalEnFinPeriode < 0:
					vals['capital_fin_periode'] = 0
				vals['engagement_garantie'] = EngagementDeGarantie
				vals['commission_garantie'] = CommissionDeGarantie
				vals['annuite'] = CapitalRembourse + interets
				somme_commission_garantie = somme_commission_garantie + CommissionDeGarantie
				amortissement_line_id = self.env['fongip.amortissement.line'].create(vals)

				CapitalEnDebutPeriode = CapitalEnFinPeriode
				Calendrier = Calendrier + relativedelta(months=+NbMoisEntreEcheance)
				"""new_calendrier = str(Calendrier)
				calendrier_split = new_calendrier.split('-')
				for i in range(0,3):
					calendrier_split[i] = int(calendrier_split[i])
				Calendrier = date(calendrier_split[0], calendrier_split[1])"""
			return True


	"""@api.onchange('montant','quotite')
	def onchange_montant_quotite(self):
		if self.montant >0 and self.quotite > 0:
			self.montant_garantie = (self.montant * self.quotite) / 100.0"""

	def compute_commission(self):
		#supprimer les factures
		commission_ids = self.env['fongip.commission'].search([('credit_garantie_id','=',self.id)])
		if 	commission_ids:
			commission_ids.unlink()
		#dictinct_duree_list = []
		taux_commission = self.taux_commission
		quotite = self.quotite
		capitalEnDebutPeriode = self.montant
		taux = self.taux / 100.0
		duree = self.duree
		CapitalRembourse = 0	
		interet = 0
		capitalEnFinPeriode=0
		nbreMoisEntreChaqueEcheance = 12
		try:
			nombre_echeance = duree / 12.0
			montant_echeance = round(capitalEnDebutPeriode * taux / (1 -(1 + taux)**(-nombre_echeance)),0)
			nbreCycle = int(nombre_echeance)
		except ZeroDivisionError:
			print("ok")
		commission_ht = 0
		commission_ttc = 0
		
		commission = self.env['fongip.commission'].create({'credit_garantie_id' : self.id})
		for num in range(1,nbreCycle+1):
			interet = round(capitalEnDebutPeriode * taux,0)
			CapitalRembourse = montant_echeance - interet
			capitalEnFinPeriode = capitalEnDebutPeriode - CapitalRembourse
			commission_ht = round((capitalEnDebutPeriode * taux_commission * quotite) / 10000,0)
			commission_ttc = round(commission_ht * (1 + 0.17),0)
			tableau = {
							'periode': "Année "+str(num),
							'capital_debut_periode':capitalEnDebutPeriode,
							'capital_rembourse':CapitalRembourse,
							'interet':interet,
							'capital_fin_periode':capitalEnFinPeriode,
							'commission_ht':commission_ht,
							'commission_ttc':commission_ttc,
							'commission_id':commission.id
				}
			if capitalEnFinPeriode < 0:
				tableau['capital_fin_periode'] = 0
			self.env['fongip.commission_line'].create(tableau)
			capitalEnDebutPeriode  = capitalEnFinPeriode
		if duree % 12 != 0:#nombre_echeance > nbreCycle:
			interet = round(capitalEnDebutPeriode * taux,0)
			CapitalRembourse = montant_echeance - interet
			CapitalEnFinPeriode = capitalEnDebutPeriode - CapitalRembourse
			commission_ht = round((capitalEnDebutPeriode * taux_commission * quotite) / 10000,0)
			commission_ttc = round(commission_ht * (1 + 0.17),0)
			tableau = {
							'periode': "Année "+str(nbreCycle + 1),
							'capital_debut_periode':capitalEnDebutPeriode,
							'capital_rembourse':CapitalRembourse,
							'interet':interet,
							'capital_fin_periode':0,
							'commission_ht':commission_ht,
							'commission_ttc':commission_ttc,
							'commission_id':commission.id
			}
			self.env['fongip.commission_line'].create(tableau)
			capitalEnDebutPeriode  = capitalEnFinPeriode#capitalEnDebutPeriode - CapitalRembourse
			#commission_ht = round((capitalEnDebutPeriode * taux_commission * quotite) / 10000,0)
			#commission_ttc = round(commission_ht * (1 + 0.17),0)
		commissions_garantie = self.env['fongip.commission'].search([('credit_garantie_id','=',self.id)])
		if commissions_garantie:
			self.montant_commission = sum(commissions_garantie.mapped('commission_ttc'))
			#sum(record.amortissement_line_ids.mapped(lambda r: r.annuite if r.status =='impaye' else 0))

class FongipCreditImpaye(models.Model):
	_name = 'fongip.credit.impaye'
	_description = 'Credits impayes'

	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	echeance_id = fields.Many2one('fongip.amortissement.line' , string="Echéance" , ondelete='cascade')
	#name = fields.Char(string="Description")
	echeance = fields.Date(related='echeance_id.echeance',string="Echeance")
	capital_debut_periode = fields.Monetary(related='echeance_id.capital_debut_periode',string='Capital restant du')
	interet = fields.Monetary(related='echeance_id.interet',string='Interet')
	annuite = fields.Monetary(related='echeance_id.annuite' , string='Annuité')

	#date_reporting = fields.Date(string="Date de reporting")
	#montant = fields.Float(string="Montant" , digits=(12,0) , compute="_compute_montant_impaye" ,store=True)
	#montant = fields.Float(string="Montant" , digits=(12,0))
	credit_garantie_id = fields.Many2one('fongip.credit' , string='credit' , ondelete='cascade')
	#date_echeance = fields.Date(string="Date d'échéance")
	#date_premiere_echeance = fields.Date(string='Date de la première échéance impayée' , required=True)
	#date_derniere_echeance = fields.Date(string='Date de dernière échéance impayée' , required=True)
	#nombre_echeances = fields.Integer(string="Nombre d'échéances " , default=1)
	date_regularisation = fields.Date(string="Date de régularisation")
	#montant_regularisation = fields.Float(string="Montant de la régularisation" , digits=(12,0))
	state = fields.Selection([('non_regularise',"Non régularisé"),('regularise',"Régularisé")] , "Régularisation",default='non_regularise')

	def regulariser(self):
		for record in self:
			record.state = "regularise"
			record.date_regularisation = fields.Date.context_today(self)


	"""@api.model
	def create(self,data):
		etat_credit_id = self.env['fongip.etat_credit'].search([('name','like','Impayé')],limit=1).id
		if etat_credit_id:
			credit = self.env['fongip.credit'].browse(data['credit_garantie_id'])
			credit.write({'etat_credit_id':etat_credit_id})
			amortissement_line_ids = credit.amortissement_line_ids
			calendrier = fields.Date.from_string(data['date_premiere_echeance'])
			#date_derniere_echeance = fields.Date.from_string(data['date_derniere_echeance'])
			NbMoisEntreEcheance = int(credit.type_remboursement)
			nombre_echeances = int(data['nombre_echeances'])
			print "========================"
			print amortissement_line_ids
			#print self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',self.credit_garantie_id.id),('echeance','=',data['date_premiere_echeance'])],limit=1)
			print "============================"
			self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',credit.id),('echeance','=',data['date_premiere_echeance'])],limit=1).write({'status':'impaye'})
			self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',credit.id),('echeance','=',data['date_derniere_echeance'])],limit=1).write({'status':'impaye'})
			for i in range(nombre_echeances -2):
				calendrier = calendrier + relativedelta(months=+NbMoisEntreEcheance)
				self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',credit.id),('echeance','=',fields.Date.to_string(calendrier))],limit=1).write({'status':'impaye'})
		return super(FongipCreditImpaye,self).create(data)"""

	"""def regulariser(self):
		etat_credit_id = self.env['fongip.etat_credit'].search([('name','like','Sain')],limit=1).id
		nombre_echeances_impayes = 0
		montant_impayes = 0
		for record in self:
			record.state='regularise'
			record.date_regularisation = fields.Date.context_today(self)
			if record.credit_garantie_id.montant_impayes == record.montant:
				#mettre a jour le tableau amortissement paye_totalement
				calendrier = fields.Date.from_string(record.date_premiere_echeance)
				NbMoisEntreEcheance = int(record.credit_garantie_id.type_remboursement)
				nombre_echeances = int(record.nombre_echeances)
				if etat_credit_id:
					record.credit_garantie_id.write({'etat_credit_id':etat_credit_id,'montant_impayes':0,'nombre_echeances_impayes':0})
					self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.credit_garantie_id.id),('echeance','=',record.date_premiere_echeance)],limit=1).write({'status':'paye_totalement'})
					self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.credit_garantie_id.id),('echeance','=',record.date_derniere_echeance)],limit=1).write({'status':'paye_totalement'})
					for i in range(nombre_echeances -2):
						calendrier = calendrier + relativedelta(months=+NbMoisEntreEcheance)
						self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.credit_garantie_id.id),('echeance','=',fields.Date.to_string(calendrier))],limit=1).write({'status':'paye_totalement'})
			else :
				nombre_echeances_impayes = record.credit_garantie_id.nombre_echeances_impayes - record.nombre_echeances
				montant_impayes = record.credit_garantie_id.montant_impayes - record.montant
				record.credit_garantie_id.write({'montant_impayes':montant_impayes,'nombre_echeances_impayes':nombre_echeances_impayes})"""


	"""def regulariser_partiellement(self,montant):
		montant_impayes = 0
		for record in self:
			record.state='paye_partiel'
			montant_impayes = record.credit_garantie_id.montant_impayes - montant
			nombre_echeances_impayes = round(montant_impayes / record.credit_garantie_id.montant_echeance,0)
			record.credit_garantie_id.write({'montant_impayes':montant_impayes,'nombre_echeances_impayes':nombre_echeances_impayes})
			record.montant = record.montant - montant
			#echeance a regulariser
			nombre_echeance_a_regulariser = record.nombre_echeances - nombre_echeances_impayes
			calendrier = fields.Date.from_string(record.date_premiere_echeance)
			NbMoisEntreEcheance = int(record.credit_garantie_id.type_remboursement)
			line = self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.credit_garantie_id.id),('echeance','=',record.date_premiere_echeance),('status','!=','paye_totalement')],limit=1)
			if line:
				line.write({'status':'paye_totalement'})
				nombre_echeance_a_regulariser -=1
			#self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.credit_garantie_id.id),('echeance','=',record.date_derniere_echeance)],limit=1).write({'status':'paye_totalement'})
			for i in range(record.nombre_echeances -1):
				calendrier = calendrier + relativedelta(months=+NbMoisEntreEcheance)
				line = self.env['fongip.amortissement.line'].search([('credit_garantie_id','=',record.credit_garantie_id.id),('echeance','=',fields.Date.to_string(calendrier)),('status','!=','paye_totalement')],limit=1)
				if line:
					line.write({'status':'paye_totalement'})
					nombre_echeance_a_regulariser -=1
				if nombre_echeance_a_regulariser == 0:
					break"""
			#nombre_echeances = int(record.nombre_echeances)
			#montant_impayes = record.credit_garantie_id.montant_impayes - montant 
			#record.credit_garantie_id.write({'montant_impayes':montant_impayes})

	"""@api.onchange('nombre_echeances','date_premiere_echeance','date_derniere_echeance')
	def _onchange_nbre_echeance_premiere_derniere(self):
		date_premiere_echeance = fields.Date.from_string(self.date_premiere_echeance)
		date_derniere_echeance = fields.Date.from_string(self.date_derniere_echeance)
		nombre_echeances = int(self.nombre_echeances)
		type_remboursement = int(self.credit_garantie_id.type_remboursement)

		if date_premiere_echeance and date_derniere_echeance and (((date_derniere_echeance - date_premiere_echeance).days +1) * 12/365 +1) / type_remboursement != nombre_echeances:
			self.nombre_echeances = (((date_derniere_echeance - date_premiere_echeance).days +1) * 12/365 +1) / type_remboursement
		elif nombre_echeances and date_premiere_echeance and (date_premiere_echeance + relativedelta(months=+type_remboursement*(nombre_echeances-1))) != date_derniere_echeance:
			self.date_derniere_echeance = date_premiere_echeance + relativedelta(months=+type_remboursement*(nombre_echeances - 1))
		elif nombre_echeances and date_derniere_echeance and (date_derniere_echeance + relativedelta(months=-type_remboursement*(nombre_echeances-1))) != date_premiere_echeance:
			self.date_premiere_echeance = date_derniere_echeance + relativedelta(months=-type_remboursement*(nombre_echeances - 1))"""

	"""@api.depends('credit_garantie_id.montant_echeance','nombre_echeances')
	def _compute_montant_impaye(self):
		for record in self:
			if record.nombre_echeances and record.credit_garantie_id.montant_echeance:
				record.montant = record.nombre_echeances * record.credit_garantie_id.montant_echeance

	@api.onchange('credit_garantie_id.montant_echeance','nombre_echeances')
	def _onchange_montant_impaye(self):
		for record in self:
			if record.nombre_echeances and record.credit_garantie_id.montant_echeance:
				record.montant = record.nombre_echeances * record.credit_garantie_id.montant_echeance"""

class FongipEncaissement(models.Model):
	_name = 'fongip.encaissement'
	_description = 'Encaissement'

	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	entreprise_id = fields.Many2one('res.partner',string='Entreprise',ondelete='cascade')
	project_id = fields.Many2one('fongip.project',string='Dossier',ondelete='cascade')
	credit_garantie_id = fields.Many2one('fongip.credit',string='crédit',ondelete='cascade')
	date_paiement = fields.Date(string='date de paiement')
	montant = fields.Monetary(string='Montant versé (FCFA)')
	observations = fields.Text(string='Observations')

	@api.model
	def create(self,data):
		all_impayes = self.env['fongip.credit.impaye'].search([('credit_garantie_id','=',data['credit_garantie_id']),('state','!=','regularise')])
		montant_encaisse = data['montant']
		montant_impaye = 0
		reste = 0
		while montant_encaisse >= 0:
			for impaye in all_impayes:
				if montant_encaisse >= impaye.montant:
					impaye.regulariser()
				elif montant_encaisse > 0 and montant_encaisse - impaye.montant < 0:
					impaye.regulariser_partiellement(montant_encaisse)
				montant_encaisse -= impaye.montant
			break
		return super(FongipEncaissement,self).create(data)


class FongipAmortissement(models.Model):
	_name = 'fongip.amortissement'
	_description = 'Amortissement'

	amortissement_line_id = fields.One2many('fongip.amortissement.line','amortissement_id' , string='Tableau des amortissement')

class FongipAmortissementLine(models.Model):
	_name = 'fongip.amortissement.line'
	_description = 'Amortissement Line'

	_rec_name = 'numero'

	currency_id = fields.Many2one('res.currency', 'Currency', 
        default=lambda self: self.env.company.currency_id.id)
	credit_garantie_id = fields.Many2one('fongip.credit',string='Crédit',ondelete='cascade')
	amortissement_id = fields.Many2one('fongip.amortissement','Amortissement',ondelete='cascade')
	numero = fields.Integer(string='Numéro',readonly=True)
	annuite = fields.Monetary(string='Annuité')
	interet = fields.Monetary(string='Interet')
	echeance = fields.Date(string='Echéance')
	capital_debut_periode = fields.Monetary(string='Capital restant du' )
	capital_fin_periode = fields.Monetary(string='Capital en fin de periode' )
	capital_rembourse = fields.Monetary(string='Capital amorti' )
	engagement_garantie = fields.Monetary(string='Engagement de garantie')
	commission_garantie = fields.Monetary(string='Commission de garantie')
	status = fields.Selection([('a_echoir',"À échoir"),('echu', "échu"),('paye', "Payé"),('en_retard', "En retard"), ('impaye',"Impayé")], string = "Statut de l'échéance", default = 'a_echoir')

	

	def payer(self):
		for record in self:
			record.status = 'paye'
			impaye = self.env['fongip.credit.impaye'].search([('echeance_id','=',record.id)])
			impaye.regulariser()
			

	def impayer(self):
		for record in self:
			record.status = 'impaye'
			#Creer un enregistrement dans Impaye
			self.env['fongip.credit.impaye'].create({'credit_garantie_id':record.credit_garantie_id.id,'echeance_id':record.id})#'montant':record.annuite
			
	