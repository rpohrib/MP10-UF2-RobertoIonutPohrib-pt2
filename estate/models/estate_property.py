from odoo import fields, models, api
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Model per estate_property'
    name = fields.Char('Nom', required=True)
    description = fields.Text('Descripció') 
    code_postal = fields.Char('Codi Postal', required=True)
    date_availability = fields.Date(
        string="Data de Disponibilitat", 
        default=lambda self: fields.Date.today() + relativedelta(months=1), 
        copy=False
    )
    selling_price_await = fields.Float('Preu de Venda Esperat', required=True)
    final_price = fields.Float('Preu de Venda Final', readonly=True, copy=False)
    best_offer = fields.Float('Millor Oferta', compute="_compute_best_offer", readonly=True, store=False)
    state = fields.Selection(
        [
            ('new', 'Nova'),
            ('offer_received', 'Oferta Rebuda'),
            ('offer_accepted', 'Oferta Acceptada'),
            ('sold', 'Venuda'),
            ('canceled', 'Cancel·lada'),
        ], 
        default='new', string="Estat"
    )
    bedrooms = fields.Integer('Nombre d\'Habitacions', required=True)
    types = fields.Many2one('estate.property.type', string="Tipus")
    tags = fields.Many2many('estate.property.tag', string="Etiquetes")
    has_elevator = fields.Boolean('Ascensor', default=False)
    has_parking = fields.Boolean('Parking', default=False)
    renovated = fields.Boolean('Renovat', default=False)
    bathrooms = fields.Integer('Banys')
    area = fields.Float('Superfície (m2)', required=True)
    price_m2 = fields.Float('Preu per m2', compute="_compute_price_per_m2", store=False)
    year_of_construction = fields.Integer('Any de Construcció')
    energy_certificate = fields.Selection(
        [('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E'), ('f', 'F'), ('g', 'G')], 
        string="Certificat Energètic"
    )
    active = fields.Boolean('Actiu', default=True)
    offers = fields.One2many('estate.property.offer', 'property_id', string="Llistat d'Ofertes")
    buyyer_id = fields.Many2one('res.partner', string="Comprador", compute='_compute_buyer', readonly=True, store=False)
    user= fields.Many2one('res.users', string="Comercial", default=lambda self: self.env.user)  # Comercial

    # Funció calcula millor oferta, preu per m2 i comprador
    @api.depends('offers.price')
    def _compute_best_offer(self):
        for record in self:
            offers = record.offers.filtered(lambda o: o.state != 'rejected')
            record.best_offer = max(offers.mapped('price'), default=0)

    # Funció calcula preu per m2
    @api.depends('selling_price_await', 'area')
    def _compute_price_per_m2(self):
        for record in self:
            record.price_m2 = record.selling_price_await / record.area if record.area else 0

    # Funció calcula comprador
    @api.depends('offers.state', 'offers.price')
    def _compute_buyer(self):
        for record in self:
            accepted_offer = record.offers.filtered(lambda o: o.state == 'accepted')
            if accepted_offer:
                best_accepted_offer = max(accepted_offer, key=lambda o: o.price)
                record.buyyer_id = best_accepted_offer.buyer_id
                record.final_price = best_accepted_offer.price
            else:
                record.buyyer_id = False
                record.final_price = 0
