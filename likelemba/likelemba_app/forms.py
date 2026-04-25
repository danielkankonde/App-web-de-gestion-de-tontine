from django import forms
from .models import Groupe
from .models import MembreGroupe, Utilisateur

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
                'placeholder': 'Téléphone'
            }),
            'ordre_reception': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ordre de réception'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.groupe = kwargs.pop('groupe')
        super().__init__(*args, **kwargs)
        self.fields['utilisateur'].required = False
        self.fields['nom'].required = False
        self.fields['utilisateur'].empty_label = "Sélectionnez un membre avec compte"
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
            raise forms.ValidationError("Cet ordre est déjà utilisé")

        return ordre

class OrdreMembreForm(forms.ModelForm):
    class Meta:
        model = MembreGroupe
        fields = ['ordre_reception']

        widgets = {
            'ordre_reception': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ordre de réception'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.groupe = kwargs.pop('groupe')
        super().__init__(*args, **kwargs)

    def clean_ordre_reception(self):
        ordre = self.cleaned_data['ordre_reception']

        # 🔐 empêcher doublon
        if MembreGroupe.objects.filter(
            groupe=self.groupe,
            ordre_reception=ordre
        ).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Cet ordre est déjà utilisé")

        return ordre
