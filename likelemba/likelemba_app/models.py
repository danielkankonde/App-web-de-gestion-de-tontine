from django.db import models

from authentification.models import Utilisateur


# =====================
# GROUPE
# =====================
class Groupe(models.Model):

    nom = models.CharField(max_length=100)

    montant_cotisation = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    frequence = models.CharField(max_length=20)

    date_debut = models.DateField()

    statut = models.CharField(
        max_length=20,
        choices=[
            ('ACTIF', 'Actif'),
            ('TERMINE', 'Terminé')
        ]
    )

    admin = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE
    )


# =====================
# MEMBRE GROUPE
# =====================
class MembreGroupe(models.Model):

    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE
    )

    groupe = models.ForeignKey(
        Groupe,
        on_delete=models.CASCADE
    )

    ordre_reception = models.IntegerField()


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