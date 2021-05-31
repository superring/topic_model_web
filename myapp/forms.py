from django import forms


class DocumentForm(forms.Form):
    num_topics = forms.IntegerField(min_value=1, max_value=100, initial=6)
    no_below = forms.IntegerField(min_value=0, max_value=10, initial=0)
    no_above = forms.FloatField(initial=0.5)
    separator = forms.fields.ChoiceField(
        choices=(
            ("1", '句読点'),
            ("2", '改行')
        ),
        required=True,
        widget=forms.widgets.Select,
        initial='1'
    )
    docfile = forms.FileField(label='ファイルを選択してください')
