from django import forms
from .models import Groupe

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