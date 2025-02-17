from odoo import models, fields

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Ofertes de propietat'
    price = fields.Float('Preu Oferit', required=True)
    state = fields.Selection( 
        [
            ('accepted', 'Acceptada'),
            ('rejected', 'Rebutjada'),
            ('pending', 'En tractament')
        ], 
        default='pending', string="Estat"
    )
    # Camp relacionat amb el comprador de la propietat
    buyer_id = fields.Many2one('res.partner', string="Comprador")
    # Comentaris 
    comments = fields.Text('Comentaris')
    # Camp relacionat amb la propietat en venda que nomes es pot llegir
    property_id = fields.Many2one('estate.property', string="Propietat", readonly=True)  
    # Funció per acceptar una oferta
    def action_accept(self):
        self.ensure_one()
        self.state = 'accepted'
        self.property_id.final_price = self.price
        self.property_id.buyyer_id = self.buyer_id
        self.property_id.state = 'offer_accepted'
    # Funció per rebutjar una oferta
    def action_reject(self):
        self.ensure_one()
        self.state = 'rejected'
        # Mirem si hi ha alguna altra oferta que esta aceptada
        other_accepted_offer = self.property_id.offers.filtered(lambda o: o.state == 'accepted' and o.id != self.id)
        if self.property_id.final_price == self.price:
            if other_accepted_offer:
                self.property_id.final_price = other_accepted_offer[0].price 
                self.property_id.buyyer_id = other_accepted_offer[0].buyer_id
            else:
                self.property_id.final_price = 0
                self.property_id.buyyer_id = False
                self.property_id.state = 'new'
