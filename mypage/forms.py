from .models import DstagramPhoto, Comment, Dstagram, Search
from django import forms

class DstagramForm(forms.ModelForm):
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple':True}), label='사진')
    content = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "#으로 태그를 달아보세요",\
                                                'style':"min-width:100px; min-height:200px;"}), label='text')
    
    class Meta:
        model = Dstagram
        fields = []
    
class SearchForm(forms.ModelForm):
    class Meta:
        model = Search
        fields = ['search']

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.fields['search'].widget.attrs['class']='textfield-search'
        self.fields['search'].widget.attrs['placeholder']='search...'
        self.fields['search'].widget.attrs['rows']=1
        self.fields['search'].label=''


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)

        self.fields['content'].widget.attrs['class']='textfield-comment'
        self.fields['content'].widget.attrs['placeholder']='댓글 달기...'
        self.fields['content'].label=''
        self.fields['content'].widget.attrs['rows']=1