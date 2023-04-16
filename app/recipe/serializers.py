"""
Serializers for recipe API
"""

from rest_framework import serializers
from core.models import (
    Recipe,
    Tag,
    Ingrediant,
)


class IngrediantSerializer(serializers.ModelSerializer):
    """Serializer for ingrediants"""

    class Meta:
        model =Ingrediant
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""
    tags = TagSerializer(many=True, required=False)
    ingrediants = IngrediantSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingrediants',
            ]

        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag in tags :
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )

            recipe.tags.add(tag_obj)

    def _get_or_create_ingrediants(self, ingrediants, recipe):
        """Handle getting or creating ingrediants as needed"""
        auth_user = self.context['request'].user
        for ingrediant in ingrediants:
            ingrediant_obj, created = Ingrediant.objects.get_or_create(
                user=auth_user,
                **ingrediant
            )

            recipe.ingrediants.add(ingrediant_obj)

    def create(self, valdiated_data):
        """Create a recipe """
        tags = valdiated_data.pop('tags', [])
        ingrediants = valdiated_data.pop('ingrediants', [])
        recipe = Recipe.objects.create(**valdiated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingrediants(ingrediants, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe"""
        tags = validated_data.pop('tags', None)
        ingrediants = validated_data.pop('ingrediants', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingrediants is not None:
            instance.ingrediants.clear()
            self._get_or_create_ingrediants(ingrediants, instance)


        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
