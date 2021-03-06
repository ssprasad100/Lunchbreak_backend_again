from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .models import (DeliveryPeriod, Food, FoodType, HolidayPeriod, Ingredient,
                     IngredientGroup, IngredientRelation, Menu, OpeningPeriod,
                     Quantity, Region, Store, StoreCategory, StoreHeader)


@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


class StoreHeaderThumbnail:

    def thumbnail(self, obj):
        return '<img src="{}"/>'.format(
            reverse('customers:store-header', kwargs={
                'store_id': obj.store.id,
                'width': 100,
                'height': 100
            })
        )
    thumbnail.short_description = _('Voorbeeld')
    thumbnail.allow_tags = True


@admin.register(StoreHeader)
class StoreHeaderAdmin(admin.ModelAdmin, StoreHeaderThumbnail):
    list_display = ('store', 'thumbnail',)
    readonly_fields = (
        'thumbnail', 'ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi',
    )
    fields = ('store', 'original',) + readonly_fields


class StoreHeaderInline(admin.StackedInline, StoreHeaderThumbnail):
    model = StoreHeader

    readonly_fields = ('thumbnail',)
    fields = ('original', 'thumbnail',)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'wait', 'enabled',)
    readonly_fields = ('timezone', 'latitude', 'longitude', 'hearts',)
    search_fields = ('name', 'city', 'street', 'country')
    list_filter = ('city', 'country', 'enabled',)
    ordering = ('name',)
    inlines = (StoreHeaderInline,)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'postcode',)
    search_fields = ('name', 'country', 'postcode',)
    ordering = ('country', 'name',)


class PeriodAdmin(admin.ModelAdmin):
    list_display = ('store', 'day', 'time', 'duration',)
    search_fields = ('store__name',)
    list_filter = ('day', 'store',)
    ordering = ('store__name', 'day',)


admin.site.register(OpeningPeriod, PeriodAdmin)
admin.site.register(DeliveryPeriod, PeriodAdmin)


@admin.register(HolidayPeriod)
class HolidayPeriodAdmin(admin.ModelAdmin):
    list_display = ('store', 'start', 'end', 'closed',)
    search_fields = ('store__name', 'description',)
    list_filter = ('closed', 'store',)
    ordering = ('store__name', 'start', 'end', 'closed',)


@admin.register(FoodType)
class FoodTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'quantifier', 'inputtype',)
    search_fields = ('name', 'quantifier',)
    list_filter = ('store', 'inputtype',)
    ordering = ('name', 'store', 'inputtype',)

    fieldsets = (
        (
            _('Basis informatie'),
            {
                'fields': (
                    'name',
                    'inputtype',
                    'store',
                    'quantifier',
                ),
            },
        ),
        (
            _('Bestel instellingen'),
            {
                'fields': (
                    'wait',
                    'preorder_time',
                    'preorder_days',
                )
            },
        ),
    )


@admin.register(IngredientGroup)
class IngredientGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'priority', 'calculation', 'foodtype',)
    search_fields = ('name', 'store__name', 'ingredients__name',
                     'ingredients__food__name', 'foodtype__name',)
    list_filter = ('calculation', 'foodtype__inputtype', 'store',)
    ordering = ('store__name', 'priority', 'name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'group', 'last_modified',)
    search_fields = ('name', 'group__store__name', 'group__name',)
    list_filter = ('group__store',)
    ordering = ('group__store__name', 'name', 'group__name', 'last_modified',)
    readonly_fields = ('store',)

    def store(self, obj):
        return obj.group.store
    store.short_description = _('winkel')

    fieldsets = (
        (
            _('Basis informatie'),
            {
                'fields': (
                    'name',
                    'cost',
                    'group',
                    'store',
                ),
            },
        ),
    )


@admin.register(Quantity)
class QuantityAdmin(admin.ModelAdmin):
    list_display = ('store', 'foodtype', 'minimum', 'maximum', 'last_modified',)
    search_fields = ('store__name', 'foodtype_name',)
    list_filter = ('store',)
    ordering = ('store__name', 'foodtype__name', 'last_modified',)


class IngredientsRelationInline(admin.TabularInline):
    model = IngredientRelation
    extra = 1
    fields = ('ingredient', 'selected', 'typical', 'cost', 'group_cost',)
    readonly_fields = ('typical', 'cost', 'group_cost',)

    def cost(self, obj):
        return obj.ingredient.cost
    cost.short_description = _('kostprijs')

    def group_cost(self, obj):
        return obj.ingredient.group.cost
    group_cost.short_description = _('kostprijs groep')

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'ingredient':
            # dirty trick so queryset is evaluated and cached in .choices
            formfield.choices = formfield.choices
        return formfield


class FoodForm(forms.ModelForm):

    class Meta:
        model = Food
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk is not None:
            ingredientgroups = IngredientGroup.objects.filter(
                store_id=self.instance.menu.store_id
            )
            self.fields['ingredientgroups'].queryset = ingredientgroups


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    form = FoodForm
    list_display = ('name', 'store', 'menu', 'priority', 'cost', 'preorder_disabled',)
    inlines = (IngredientsRelationInline,)
    search_fields = ('name', 'menu__store__name', 'menu__name',)
    list_filter = ('menu__store', 'preorder_disabled', 'preorder_days', 'preorder_time',)
    ordering = ('menu__store__name', 'name', 'priority',)
    readonly_fields = ('store', 'last_modified')

    def store(self, obj):
        return obj.menu.store
    store.short_description = _('winkel')

    fieldsets = (
        (
            _('Basis informatie'),
            {
                'fields': (
                    'name',
                    'description',
                    'cost',
                    'amount',
                    'priority',
                    'commentable',
                    'enabled',
                    'last_modified',
                ),
            },
        ),
        (
            _('Inhoud'),
            {
                'fields': (
                    'foodtype',
                    'menu',
                    'ingredientgroups',
                ),
            },
        ),
        (
            _('Bestel instellingen'),
            {
                'fields': (
                    'wait',
                    'preorder_time',
                    'preorder_days',
                    'preorder_disabled',
                )
            },
        ),
    )


class BaseTokenAdmin(admin.ModelAdmin):
    list_display = ('device', 'service',)
    list_filter = ('service',)


class FoodInline(admin.StackedInline):
    model = Food
    extra = 0

    form = FoodForm
    inlines = (IngredientsRelationInline,)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'priority',)
    search_fields = ('name', 'store__name',)
    list_filter = ('store',)
    ordering = ('store__name', 'priority', 'name',)
    inlines = (FoodInline,)
