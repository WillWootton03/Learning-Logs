from django import forms
from django.forms.models import ModelForm

from .models import Board


class NewBoard(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'description']
        widgets = {
            'title' : forms.TextInput(attrs={
                'placeholder' : 'Board Title',
                'required' : True,
                'id' : 'title',
                'class' : " text-center text-2xl font-bold block w-full rounded-md h-16 border-3 border-purple-700 bg-white/5 px-3 py-1.5 text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-purple-500"
            }),
            'description' : forms.TextInput(attrs={
                'placeholder' : 'Board Description',
                'required' : True,
                'id' : 'description',
                'class' : "text-center text-base block w-full rounded-md h-20 bg-white/5 px-3 py-1.5 border-3 border-purple-700 text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-purple-500"
            }),

        }
        