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
                'class' : "text-white font-bold text-2xl w-[98%] h-[80%] bg-transparent px-2 py-3 inline-block text-center focus:outline-none resize-none rounded-b-2xl active:border-none active:radius-none"
            }),
            'content' : forms.Textarea(attrs={
                'placeholder' : 'Enter Log Here',
                'required' : True,
                'spellcheck' : 'true',
                'id' : 'content',
                'class': 'bg-gray-700 w-full h-[95%] px-3 py-1.5 leading-[2rem] text-white font-medium placeholder:text-gray-50 focus:outline-none resize-none rounded-b-2xl active:border-none active:radius-none',
                'style': 'background-image: repeating-linear-gradient(to bottom, rgba(255,255,255,0.25) 0, rgba(255,255,255,0.25) 1px, transparent 1px, transparent 2rem);',
            }),
        }