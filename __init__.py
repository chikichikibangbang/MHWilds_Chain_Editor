from .addons.MHWilds_Chain_Editor import register as addon_register, unregister as addon_unregister

bl_info = {
    "name": 'MHWilds Chain Editor',
    "author": 'NSA Cloud, alphaZomega, 诸葛不太亮',
    "version": (1, 0),
    "blender": (2, 93, 0),
    "description": 'Import, edit and export MHWilds chain2 & clsp files.',
    "warning": '',
    "wiki_url": 'https://github.com/chikichikibangbang/MHWilds_Chain_Editor',
    "tracker_url": 'https://github.com/chikichikibangbang/MHWilds_Chain_Editor/issues',
    "support": 'COMMUNITY',
    "category": 'Import-Export'
}

def register():
    addon_register()

def unregister():
    addon_unregister()

    