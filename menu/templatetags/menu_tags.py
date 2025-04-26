from django import template
from django.urls import reverse, NoReverseMatch
from menu.models import MenuItem, Menu
from django.urls import resolve

register = template.Library()

@register.inclusion_tag('menu/menu.html', takes_context=True)
def draw_menu(context, menu_name):
    try:
        menu = Menu.objects.get(name=menu_name)
    except Menu.DoesNotExist:
        return {'menu_items': []}

    current_path = context['request'].path
    current_url_name = resolve(current_path).url_name

    all_items = menu.items.select_related('parent').all()

    def build_tree(parent=None):
        branch = []
        for item in all_items:
            if item.parent == parent:
                branch.append({
                    'item': item,
                    'children': build_tree(item),
                    'active': is_active(item),
                    'expanded': is_expanded(item)
                })
        return branch

    def is_active(item):
        try:
            return reverse(item.named_url) == current_path if item.named_url else item.url == current_path
        except:
            return item.url == current_path

    def is_expanded(item):
        return any(
            is_active(child['item']) or is_expanded(child['item'])
            for child in build_tree(item)
        )

    tree = build_tree()
    return {'menu_items': tree}