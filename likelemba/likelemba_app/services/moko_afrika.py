import logging
import os
import requests
from decimal import Decimal, InvalidOperation
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone
from likelemba_app.models import (TransactionMobileMoney, Paiement, Tour,)
from django.views.decorators.csrf import csrf_exempt
    
logger = logging.getLogger(__name__)
# Fonction pour initier une demande de cotisation auprès de Moko Afrika
def initier_cotisation(
    montant,
    devise,
    telephone,
    prenom,
    nom,
    email,
    reference,
    methode,
    callback_url="",
):
    """
    Initialise une demande de cotisation Mobile Money.
    Une réponse positive signifie que la demande a été reçue,
    pas que le paiement est terminé.
    """

    try:
        montant = Decimal(str(montant))
    except (InvalidOperation, ValueError):
        raise ValueError("Le montant est invalide.")

    if montant <= 0:
        raise ValueError("Le montant doit être supérieur à zéro.")

    if devise not in ("CDF", "USD"):
        raise ValueError("Devise non prise en charge.")

    methodes_autorisees = {
        "mpesa",
        "orange",
        "airtel",
        "afrimoney",
    }

    if methode not in methodes_autorisees:
        raise ValueError("Méthode Mobile Money non prise en charge.")

    merchant_id = os.environ.get("MOKO_MERCHANT_ID")
    merchant_secret = os.environ.get("MOKO_MERCHANT_SECRET")
    base_url = os.environ.get("MOKO_BASE_URL")

    if not all([merchant_id, merchant_secret, base_url]):
        raise RuntimeError(
            "La configuration Moko Afrika est incomplète."
        )

    donnees = {
        "merchant_id": merchant_id,
        "merchant_secrete": merchant_secret,
        "action": "debit",
        "method": methode,
        "amount": str(montant),
        "currency": devise,
        "customer_number": telephone,
        "firstname": prenom,
        "lastname": nom,
        "email": email,
        "reference": reference,
        "callback_url": callback_url,
    }

    reponse = requests.post(
        base_url,
        json=donnees,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )

    if not reponse.ok:
        logger.error(
            "Erreur Moko Afrika : HTTP %s - Réponse : %s",
            reponse.status_code,
            reponse.text
        )
        reponse.raise_for_status()

    return reponse.json()

# Fonction pour vérifier le statut d'une cotisation auprès de Moko Afrika
def verifier_cotisation(reference):
    """Vérifie le statut d'une transaction auprès de Moko Afrika."""

    merchant_id = os.environ.get("MOKO_MERCHANT_ID")
    merchant_secret = os.environ.get("MOKO_MERCHANT_SECRET")
    base_url = os.environ.get("MOKO_BASE_URL")

    if not all([merchant_id, merchant_secret, base_url]):
        raise RuntimeError("Configuration Moko Afrika incomplète.")

    if not reference or not reference.strip():
        raise ValueError("La référence est obligatoire.")

    donnees = {
        "merchant_id": merchant_id,
        "merchant_secrete": merchant_secret,
        "action": "verify",
        "reference": reference.strip(),
    }

    reponse = requests.post(
        base_url,
        json=donnees,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )

    reponse.raise_for_status()
    resultat = reponse.json()

    return {
        "reference": resultat.get("Reference"),
        "statut": resultat.get("Trans_Status"),
        "montant": resultat.get("Amount"),
        "devise": resultat.get("Currency"),
        "transaction_id": resultat.get("Transaction_id"),
        "action": resultat.get("Action"),
        "methode": resultat.get("Method"),
        "trouvee": resultat.get("Status") == "Success",
    }
# Fonction pour confirmer une cotisation après vérification auprès de Moko Afrika
def confirmer_cotisation(reference):
    """
    Confirme une cotisation après vérification auprès de Moko Afrika.
    """

    with transaction.atomic():

        # 1. Retrouver et verrouiller la transaction
        transaction_mm = (
            TransactionMobileMoney.objects
            .select_for_update()
            .select_related("membre", "tour")
            .get(reference=reference)
        )

        # 2. Éviter un traitement en double
        if transaction_mm.statut == "PAYEE":
            return {
                "succes": True,
                "message": "Cette cotisation est déjà confirmée."
            }

        # 3. Vérifier auprès de Moko Afrika
        resultat = verifier_cotisation(transaction_mm.reference)

        if not resultat["trouvee"]:
            return {
                "succes": False,
                "message": "Transaction introuvable chez Moko Afrika."
            }

        if resultat["statut"] != "Successful":
            if resultat["statut"] == "Failed":
                transaction_mm.statut = "ECHEC"
                transaction_mm.save(
                    update_fields=["statut", "date_modification"]
                )

            return {
                "succes": False,
                "message": "Le paiement n'est pas encore confirmé."
            }

        # 4. Vérifier la référence et le type de transaction
        if resultat["reference"] != transaction_mm.reference:
            raise ValueError("La référence de transaction ne correspond pas.")

        if resultat["action"] != "debit":
            raise ValueError("Cette transaction n'est pas une collecte.")

        # 5. Vérifier le montant et la devise
        montant_recu = Decimal(str(resultat["montant"]))

        if montant_recu != transaction_mm.montant:
            raise ValueError("Le montant reçu ne correspond pas.")

        if resultat["devise"] != transaction_mm.devise:
            raise ValueError("La devise reçue ne correspond pas.")

        # 6. Vérifier le membre et le tour
        tour = transaction_mm.tour

        if tour.membre_id != transaction_mm.membre_id:
            raise ValueError("Le membre ne correspond pas au tour.")

        if tour.statut == "PAYE":
            raise ValueError("Ce tour est déjà payé par une autre opération.")

        # 7. Vérifier qu'aucun paiement n'existe déjà pour ce tour
        paiement_existant = Paiement.objects.filter(tour=tour).exists()

        if paiement_existant:
            raise ValueError("Un paiement existe déjà pour ce tour.")

        # 8. Enregistrer le paiement confirmé
        Paiement.objects.create(
            membre=transaction_mm.membre,
            tour=tour,
            montant=transaction_mm.montant,
            date_paiement=timezone.localdate(),
            statut="PAYE",
        )

        # 9. Mettre à jour le tour
        tour.statut = "PAYE"
        tour.save(update_fields=["statut"])

        # 10. Mettre à jour la transaction Mobile Money
        transaction_mm.statut = "PAYEE"
        transaction_mm.identifiant_fournisseur = (
            resultat.get("transaction_id") or ""
        )

        transaction_mm.save(
            update_fields=[
                "statut",
                "identifiant_fournisseur",
                "date_modification",
            ]
        )

        return {
            "succes": True,
            "message": "Cotisation confirmée avec succès."
        }
    
@csrf_exempt
@require_POST
def moko_webhook(request):
    try:
        donnees = json.loads(request.body.decode("utf-8"))

        reference = donnees.get("PayDRC_Reference") or donnees.get("Reference")

        if not reference:
            return HttpResponse(
                "Référence manquante",
                status=400
            )

        transaction_mm = TransactionMobileMoney.objects.filter(
            reference=reference
        ).first()

        if not transaction_mm:
            return HttpResponse(
                "Transaction introuvable",
                status=404
            )

        # Vérification auprès de Moko Afrika
        confirmer_cotisation(reference)

        return HttpResponse("Webhook reçu", status=200)

    except json.JSONDecodeError:
        return HttpResponse("JSON invalide", status=400)

    except Exception:
        logger.exception("Erreur lors du traitement du webhook Moko Afrika")
        return HttpResponse("Erreur interne", status=500)
