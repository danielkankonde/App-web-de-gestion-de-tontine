from django.db import models

from authentification.models import Utilisateur


# =====================
# GROUPE
# =====================
class Groupe(models.Model):

    FREQUENCE_CHOICES = [
        ('QUOTIDIEN', 'Quotidien'),
        ('HEBDOMADAIRE', 'Hebdomadaire'),
        ('MENSUEL', 'Mensuel'),
        ('ANNUEL', 'Annuel')
    ]

    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('TERMINE', 'Terminé')
    ]

    nom = models.CharField(max_length=100)

    montant_cotisation = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    frequence = models.CharField(max_length=20, choices=FREQUENCE_CHOICES)

    date_debut = models.DateField()

    statut = models.CharField(max_length=20, choices = STATUT_CHOICES, default='ACTIF')

    date_creation = models.DateTimeField(auto_now_add=True, null=True)

    admin = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.nom


# =====================
# MEMBRE GROUPE
# =====================
class MembreGroupe(models.Model):

    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    groupe = models.ForeignKey(
        Groupe,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    nom = models.CharField(max_length=100, null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True)

    ordre_reception = models.IntegerField()

    @property
    def nom_affiche(self):
        if self.utilisateur:
            return self.utilisateur.username
        return self.nom or "Membre sans nom"

    def __str__(self):
        return f'{self.nom_affiche} - groupe : {self.groupe}'
    
    class Meta:
        unique_together = ('utilisateur', 'groupe')


# =====================
# PAIEMENT
# =====================
class Paiement(models.Model):

    membre = models.ForeignKey(
        MembreGroupe,
        on_delete=models.CASCADE
    )

    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    date_paiement = models.DateField()

    statut = models.CharField(
        max_length=20,
        choices=[
            ('PAYE', 'Payé'),
            ('NON_PAYE', 'Non payé')
        ]
    )

    def __str__(self):
        return f'{self.membre} - Paiement : {self.montant}'


# =====================
# TOUR
# =====================
class Tour(models.Model):

    groupe = models.ForeignKey(
        Groupe,
        on_delete=models.CASCADE
    )

    numero_tour = models.IntegerField()

    beneficiaire = models.ForeignKey(
        MembreGroupe,
        on_delete=models.CASCADE
    )

    date_tour = models.DateField()

    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.beneficiaire
