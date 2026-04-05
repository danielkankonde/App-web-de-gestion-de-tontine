from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Groupe

# On récupère ton modèle Utilisateur personnalisé
User = get_user_model()

class LikelembaGroupeTests(TestCase):

    def setUp(self):
        """Configuration initiale avant chaque test"""
        # 1. Créer un utilisateur avec le rôle ADMIN pour passer la sécurité
        self.admin_user = User.objects.create_user(
            username='daniel_admin',
            email='daniel@test.com',
            password='password123',
            role='ADMIN'  # Important car ta vue vérifie request.user.role
        )
        
        # 2. On connecte l'utilisateur au client de test
        self.client.login(username='daniel_admin', password='password123')
        
        # 3. URL de la vue (le nom défini dans ton path)
        self.url_creation = reverse('create_groupe')

    def test_creation_groupe_reussie(self):
        """Test fonctionnel : Création d'un groupe via le formulaire"""
        
        # Données simulant le formulaire POST
        data = {
            'nom': 'Likelemba Victoire',
            'montant_cotisation': 50000.00,
            'frequence': 'MENSUEL',
            'date_debut': '2026-05-01',
            'statut': 'ACTIF'
        }

        # On simule l'envoi du formulaire
        response = self.client.post(self.url_creation, data)

        # Vérifications (Assertions)
        # 1. Vérifie que l'app nous redirige vers la liste des groupes avec un code 302
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('liste_groupes'))

        # 2. Vérifie que le groupe existe bien en base de données
        self.assertEqual(Groupe.objects.count(), 1)
        
        # 3. Vérifie que l'admin assigné est bien l'utilisateur connecté
        groupe_cree = Groupe.objects.first()
        self.assertEqual(groupe_cree.nom, 'Likelemba Victoire')
        self.assertEqual(groupe_cree.admin, self.admin_user)

    def test_acces_interdit_si_pas_admin(self):
        """Sécurité : Un utilisateur 'MEMBRE' ne doit pas pouvoir créer de groupe"""
        # Créer un simple membre et le connecter
        membre = User.objects.create_user(
            username='membre_test',
            password='password123',
            role='MEMBRE'
        )
        self.client.login(username='membre_test', password='password123')

        response = self.client.get(self.url_creation)

        # Vérifie qu'il est redirigé vers le dashboard_membre comme prévu dans ta vue
        self.assertRedirects(response, reverse('dashboard_membre'))