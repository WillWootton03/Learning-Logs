from django import forms
from .models import Log

class NewLog(forms.ModelForm):
    class Meta:
        model = Log
        fields = ['title', 'content']
        widgets = {
            'title' : forms.TextInput(attrs={
                'placeholder' : 'Log Title',
                'required' : True,
                'id' : 'title',
                'class' : "bg-green-800 text-white px-2 py-3 text-center w-full rounded-2xl font-bold text-2xl"
            }),
            'content' : forms.Textarea(attrs={
                'placeholder' : 'Enter Log Here',
                'required' : True,
                'spellcheck' : 'true',
                'id' : 'content',
                'class': 'bg-green-800 w-full h-full px-3 py-1.5 leading-[2rem] text-white font-medium placeholder:text-gray-50 focus:outline-none resize-none rounded-b-2xl',
                'style': 'background-image: repeating-linear-gradient(to bottom, rgba(255,255,255,0.25) 0, rgba(255,255,255,0.25) 1px, transparent 1px, transparent 2rem);',
            }),
        }