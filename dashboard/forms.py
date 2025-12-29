from django import forms

from .models import Board, Tag, Concept


class NewBoard(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'description']
        widgets = {
            'title' : forms.TextInput(attrs={
                'placeholder' : 'Board Title',
                'required' : True,
                'id' : 'title',
                'class' : " text-center text-white text-2xl font-bold w-[95%] h-full bg-transparent focus:outline-none"
            }),
            'description' : forms.TextInput(attrs={
                'placeholder' : 'Board Description',
                'required' : True,
                'id' : 'description',
                'class' : "text-center text-white text-lg w-[95%] h-[95%] bg-transparent focus:outline-none"
            }),

        }

class NewConcept(forms.ModelForm):
    class Meta:
        model = Concept
        fields = ['answer', 'definition', 'hint']
        widgets = {
            'answer' : forms.TextInput(attrs={
                'placeholder' : 'Concept Answer',
                'id' : 'answer',
                'required' : True,
                'class' : "text-2xl text-white placeholder:text-gray-300 bg-transparent w-[98%] h-fit text-center focus:outline-none"
            }),
            'definition' : forms.Textarea(attrs={
                'placeholder' : 'Concept Definition',
                'id' : 'description',
                'required' : True,
                 "class" : "resize-none text-lg text-white bg-transparent w-[98%] h-[80%] text-center align-content-center focus:outline-none"
            }),
            'hint' : forms.Textarea(attrs={
                'placeholder' : "Concept Hint",
                'id' : 'hint',
                'required' : True,
                "class" : "resize-none text-lg text-white bg-transparent w-[98%] h-[70%] text-center align-content-center focus:outline-none"
            })
        }

class SetTags(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name' : forms.TextInput(attrs={
                'placeholder' : 'New Tag',
                'id' : 'tag-name',
                'name' : 'name',
                'required' : True,
                'class' : "text-2xl font-bold h-full w-full bg-transparent focus:outline-none",
            })
        }