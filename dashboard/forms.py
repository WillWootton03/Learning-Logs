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
                'class' : " text-center text-2xl font-bold block w-full rounded-md h-16 border-3 border-purple-700 bg-white/5 px-3 py-1.5 text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-purple-500"
            }),
            'description' : forms.TextInput(attrs={
                'placeholder' : 'Board Description',
                'required' : True,
                'id' : 'description',
                'class' : "text-center text-base block w-full rounded-md h-20 bg-white/5 px-3 py-1.5 border-3 border-purple-700 text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-purple-500"
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
                'class' : "text-2xl text-white bg-green-700 text-center py-1 rounded-3xl font-bold w-[80%]"
            }),
            'definition' : forms.Textarea(attrs={
                'placeholder' : 'Concept Definition',
                'id' : 'description',
                'required' : True,
                 "class" : "resize-none h-[55%] w-[90%] bg-green-700 focus:bg-green-900 px-4 py-4 text-center"
            }),
            'hint' : forms.Textarea(attrs={
                'placeholder' : "Concept Hint",
                'id' : 'hint',
                'required' : True,
                "class" : "resize-none h-[30%] w-[90%] bg-green-700 focus:bg-green-900 px-4 py-4 text-center"
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
                'class' : "text-2xl font-bold h-full w-full",
            })
        }