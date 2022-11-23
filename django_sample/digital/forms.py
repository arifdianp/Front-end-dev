# -*- coding: utf-8 -*-
from django import forms
from django.forms import modelformset_factory
from digital.models import PartBulkFile, Part, Appliance, PartType,\
                            Characteristics, PartImage, ApplianceFamily, \
                            UserPartFilters, ApplianceFamily, UserPartColumns,\
                            FinancialCard, ApplianceFamilyDetails, Catalogue
from jb.models import Technology, Material
from ast import literal_eval

class FinancialCardForm(forms.ModelForm):
    class Meta:
        model = FinancialCard
        exclude = ['part', 'production_cost', 'positive_obsolete_analysis', 'positive_longtail_analysis']


class ApplianceFamilyDetailsForm(forms.ModelForm):
    class Meta:
        model = ApplianceFamilyDetails
        exclude = ['organisation', 'replacement_cost']
    def __init__(self, *args,**kwargs):
        org = kwargs.pop('organisation')
        
        # initiate parent class
        super(ApplianceFamilyDetailsForm, self).__init__(*args, **kwargs)
        
        # set organisation
        self.organisation = org
        
        # disable appliance family select widget
        self.fields['appliance_family'].widget.attrs['disabled'] = True
        
    def save(self, commit=False):
        details = super(ApplianceFamilyDetailsForm, self).save(commit = False)
        details.organisation = self.organisation
        details.save()
        return details

Applianceformset = modelformset_factory(ApplianceFamilyDetails, 
                    form = ApplianceFamilyDetailsForm)
    
class PartBulkFileForm(forms.ModelForm):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'required':True}))
    part = forms.ModelChoiceField(queryset=Part.objects.none(),widget=forms.HiddenInput(attrs={'required': True}))
    type = forms.ChoiceField(choices=PartBulkFile().getTypeChoices,widget=forms.HiddenInput(attrs={'required': True}))
    class Meta:
        model = PartBulkFile
        fields = ['part', 'file', 'type']

    def __init__(self, *args, **kwargs):
        created_by = None
        if 'created_by' in kwargs:
            created_by = kwargs.pop('created_by')
        super(PartBulkFileForm, self).__init__(*args, **kwargs)
        # allow change only for a part of your organisation:
        if created_by:
            self.created_by = created_by
            self.fields['part'].queryset = Part.objects.filter(organisation__id = created_by.organisation.id)

    def save(self, type="BULK", data={}):
        partBulkFile = super(PartBulkFileForm, self).save(commit=False)
        partBulkFile.created_by = self.created_by
        partBulkFile.data = "%s"%data
        partBulkFile.type = "%s"%type
        partBulkFile.save()
        return partBulkFile

class PartImageForm(forms.ModelForm):
    image = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'required':True}))
    part = forms.ModelChoiceField(queryset=Part.objects.none(),widget=forms.HiddenInput(attrs={'required': True}))
    class Meta:
        model = PartImage
        fields = ['part', 'image']

    def __init__(self, *args, **kwargs):
        created_by = None
        if 'created_by' in kwargs:
            created_by = kwargs.pop('created_by')
        super(PartImageForm, self).__init__(*args, **kwargs)
        # allow change only for a part of your organisation:
        if created_by:
            self.created_by = created_by
            self.fields['part'].queryset = Part.objects.filter(organisation__id = created_by.organisation.id)

    def save(self):
        partImage = super(PartImageForm, self).save(commit=False)
        partImage.created_by = self.created_by
        partImage.save()
        return partImage
        
        
        
        
class PartFiltersForm(forms.ModelForm):
    # utility only

    
    printable = forms.ChoiceField(choices=UserPartFilters().getPrintableChoiceList, widget=forms.RadioSelect)
    analysis = forms.ChoiceField(choices=UserPartFilters().getAnalysisChoiceList, widget=forms.RadioSelect)
    reorder = forms.MultipleChoiceField(choices = UserPartFilters().getReorderYearChoiceList, widget=forms.CheckboxSelectMultiple(), required=False, label="Reorder needed")
    appliance_family = forms.MultipleChoiceField(choices = tuple(ApplianceFamily.objects.all().values_list("id", "name")), widget=forms.CheckboxSelectMultiple(), required=False, label="Appliance Family")
    part_type = forms.MultipleChoiceField(choices = tuple(PartType.objects.all().values_list("name", "name").distinct()), widget=forms.CheckboxSelectMultiple(), required=False, label="Part Type")
    technology = forms.MultipleChoiceField(choices = (('', 'NO TECHNOLOGY'),) + tuple(Technology.objects.all().values_list("id", "name")), widget=forms.CheckboxSelectMultiple(), required=False, label="Technology")
    material = forms.MultipleChoiceField(choices = (('', 'NO MATERIAL'),) + tuple(Material.objects.all().values_list("id", "name")), widget=forms.CheckboxSelectMultiple(), required=False, label="Material")
    
    class Meta:
        model = UserPartFilters
        exclude = ['user', 'parttype_list', 'appliance_list','technology_list','material_list', 'reorder', 'sort']
    def __init__(self, *args, **kwargs):
        user = None
        if 'user' in kwargs:
            user = kwargs.pop('user')
        if user and hasattr(user, 'part_filters'):
            kwargs['instance'] = user.part_filters
        # SUPER INIT
        super(PartFiltersForm, self).__init__(*args, **kwargs)
        
        # IF USER THEN DO THIS
        if user:
            self.user = user    
            appliance_families = tuple(ApplianceFamily.objects.filter(industry__in = user.organisation.industry.all()).order_by('name').values_list("id", "name"))
            part_types = tuple(PartType.objects.filter(appliance_family__industry__in = user.organisation.industry.all()).order_by('name').values_list("name", "name").distinct())
            # part_types =  [(pt, pt) for pt in part_types]
            self.fields['appliance_family'].choices = (('', 'NO FAMILY'),) + appliance_families
            self.fields['part_type'].choices = (('', 'NO TYPE'),) + part_types
            try:
                family_initial = literal_eval(user.part_filters.appliance_list)
            except:
                family_initial = [af[0] for af in appliance_families] + [None]
            try:
                type_initial = literal_eval(user.part_filters.parttype_list)
            except:
                type_initial = [p[0] for p in part_types] + [None]
            try:
                reorder_initial = literal_eval(user.part_filters.reorder)
            except:
                reorder_initial = []
            try:
                technology_initial = literal_eval(user.part_filters.technology_list)
            except:
                technology_initial = [t[0] for t in self.fields['technology'].choices] + [None]
            try:
                material_initial = literal_eval(user.part_filters.material_list)
            except:
                material_initial = [m[0] for m in self.fields['material'].choices] + [None]
                
            self.fields['appliance_family'].initial = family_initial
            self.fields['part_type'].initial = type_initial
            self.fields['technology'].initial = technology_initial
            self.fields['material'].initial = material_initial
            self.fields['reorder'].initial = reorder_initial
            
    def save(self):
        filters = super(PartFiltersForm, self).save(commit=False)
        if not filters.user:
            filters.user = self.user
        filters.parttype_list = "%s"%[None if x=="" else x for x in self.cleaned_data['part_type']]
        filters.appliance_list = "%s"%[None if x=="" else int(x) for x in self.cleaned_data['appliance_family']]
        filters.technology_list = "%s"%[None if x=="" else int(x) for x in self.cleaned_data['technology']]
        filters.material_list = "%s"%[None if x=="" else int(x) for x in self.cleaned_data['material']]
        filters.reorder = "%s"%[int(x) for x in self.cleaned_data['reorder']]
        filters.save()
        return filters





class PartColumnsForm(forms.ModelForm):

    class Meta:
        model = UserPartColumns
        exclude = ['user', 'production_cost']
    def __init__(self, *args, **kwargs):
        user = None
        if 'user' in kwargs:
            user = kwargs.pop('user')
        if user and hasattr(user, 'part_columns'):
            kwargs['instance'] = user.part_columns
        # SUPER INIT
        super(PartColumnsForm, self).__init__(*args, **kwargs)
        
        # IF USER THEN DO THIS
        if user:
            self.user = user    
            
    def save(self):
        columns = super(PartColumnsForm, self).save(commit=False)
        if not columns.user:
            columns.user = self.user
        columns.save()
        return columns




class PartForm(forms.ModelForm):
    # file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'required':True}))
    appliance = forms.ModelMultipleChoiceField(queryset=Appliance.objects.none(), required=False)
    type = forms.ModelChoiceField(queryset=PartType.objects.none(), required=False)
    appliance_family = forms.ModelChoiceField(queryset=ApplianceFamily.objects.none(), required=False)
    catalogue = forms.ModelChoiceField(queryset=Catalogue.objects.none(), required=False)
    class Meta:
        model = Part
        exclude = ['date_created', 'created_by', 'organisation', 'characteristics', 'status', 'final_card', 'financial_card' 'parnotify_status_to_client', 'bulk_upload']

    def __init__(self, *args, **kwargs):
        created_by = None
        if 'created_by' in kwargs:
            created_by = kwargs.pop('created_by')
        super(PartForm, self).__init__(*args, **kwargs)
        # allow change only for a part of your organisation:
        if created_by:
            self.created_by = created_by
            self.organisation = created_by.organisation
            # parts_qs = Parts.objects.filter(organisation = created_by.organisation)
            # self.fields['model'].queryset = Model.objects.filter(model_set__in = parts_qs)
            self.fields['appliance'].queryset = Appliance.objects.filter(organisation = created_by.organisation)
            self.fields['type'].queryset = PartType.objects.filter(appliance_family__industry__in = created_by.organisation.industry.all())
            self.fields['appliance_family'].queryset = ApplianceFamily.objects.filter(industry__in = created_by.organisation.industry.all())
            self.fields['catalogue'].queryset = Catalogue.objects.filter(organisation = created_by.organisation)

    def save(self, characteristics = None):
        part = super(PartForm, self).save(commit=False)
        part.created_by = self.created_by
        part.organisation = self.organisation
        if characteristics:
            part.characteristics = characteristics
        part.save()
        self.save_m2m()
        return part

class CharacteristicsForm(forms.ModelForm):
    class Meta:
        model = Characteristics
        exclude = ['part', 'technology', 'material', 'part_type', 'techno_material']
