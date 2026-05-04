from django import forms
from django.utils import timezone

from .models import Groupe, MembreGroupe, Paiement, Utilisateur


class GroupeForm(forms.ModelForm):

    class Meta:
        model = Groupe
        fields = ['nom', 'montant_cotisation', 'frequence', 'date_debut']

        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du groupe'
            }),
            'montant_cotisation': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant de cotisation'
            }),
            'frequence': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date_debut': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class MembreGroupeForm(forms.ModelForm):
    class Meta:
        model = MembreGroupe
        fields = ['utilisateur', 'nom', 'telephone', 'ordre_reception']

        widgets = {
            'utilisateur': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du membre dans le groupe'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telephone'
            }),
            'ordre_reception': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ordre de reception'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.groupe = kwargs.pop('groupe')
        super().__init__(*args, **kwargs)
        self.fields['utilisateur'].required = False
        self.fields['nom'].required = False
        self.fields['utilisateur'].empty_label = "Selectionnez un membre avec compte"
        self.fields['utilisateur'].queryset = Utilisateur.objects.filter(
            role='MEMBRE'
        ).exclude(
            membregroupe__groupe=self.groupe
        )

    def clean(self):
        cleaned_data = super().clean()
        utilisateur = cleaned_data.get('utilisateur')
        nom = (cleaned_data.get('nom') or '').strip()

        if not utilisateur and not nom:
            raise forms.ValidationError(
                "Choisissez un utilisateur existant ou saisissez le nom du membre."
            )

        cleaned_data['nom'] = nom
        return cleaned_data

    def clean_ordre_reception(self):
        ordre = self.cleaned_data['ordre_reception']

        if MembreGroupe.objects.filter(
            groupe=self.groupe,
            ordre_reception=ordre
        ).exists():
            raise forms.ValidationError("Cet ordre est deja utilise")

        return ordre


class OrdreMembreForm(forms.ModelForm):
    class Meta:
        model = MembreGroupe
        fields = ['ordre_reception']

        widgets = {
            'ordre_reception': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ordre de reception'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.groupe = kwargs.pop('groupe')
        super().__init__(*args, **kwargs)

    def clean_ordre_reception(self):
        ordre = self.cleaned_data['ordre_reception']

        if MembreGroupe.objects.filter(
            groupe=self.groupe,
            ordre_reception=ordre
        ).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Cet ordre est deja utilise")

        return ordre


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['membre', 'montant', 'date_paiement', 'statut']

        widgets = {
            'membre': forms.Select(attrs={
                'class': 'form-control'
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant paye',
                'step': '0.01'
            }),
            'date_paiement': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.groupe = kwargs.pop('groupe')
        super().__init__(*args, **kwargs)
        self.fields['membre'].queryset = MembreGroupe.objects.filter(
            groupe=self.groupe
        ).order_by('ordre_reception', 'id')
        self.fields['membre'].empty_label = "Selectionnez un membre"

        if not self.is_bound:
            self.fields['montant'].initial = self.groupe.montant_cotisation
            self.fields['date_paiement'].initial = timezone.localdate()
            self.fields['statut'].initial = 'PAYE'

    def clean_montant(self):
        montant = self.cleaned_data['montant']

        if montant <= 0:
            raise forms.ValidationError("Le montant doit etre superieur a zero.")

        return montant

    def clean_membre(self):
        membre = self.cleaned_data['membre']

        if membre.groupe_id != self.groupe.id:
            raise forms.ValidationError("Ce membre n'appartient pas a ce groupe.")

        return membre
