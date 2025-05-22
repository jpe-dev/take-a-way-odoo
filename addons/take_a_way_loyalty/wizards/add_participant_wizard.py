from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AddParticipantWizard(models.TransientModel):
    _name = 'add.participant.wizard'
    _description = 'Assistant pour ajouter un participant à une mission'

    mission_id = fields.Many2one('take_a_way_loyalty.mission', string='Mission', required=True)
    participant_id = fields.Many2one('res.partner', string='Participant', required=True, domain="[('is_company', '=', False), ('type', '=', 'contact')]")

    def action_add_participant(self):
        self.ensure_one()
        MissionUser = self.env['take_a_way_loyalty.mission_user']
        # Vérifier si le participant existe déjà
        existing = MissionUser.search([
            ('mission_id', '=', self.mission_id.id),
            ('utilisateur_id', '=', self.participant_id.id)
        ], limit=1)
        if existing:
            raise ValidationError(_('Ce participant est déjà inscrit à cette mission.'))
        # Créer le participant
        MissionUser.create({
            'mission_id': self.mission_id.id,
            'utilisateur_id': self.participant_id.id,
        })
        return {'type': 'ir.actions.act_window_close'} 