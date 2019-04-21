class Traits:

    ALLOWED_KEYS = {'visible', 'evident', 'compelling', 'portable', 'ubiquitous',
                    'composite', 'plural', 'surface', 'closed', 'locked',
                    'fragile', 'hostile', 'friendly', 'mobile', 'precarious'}

    def __init__(self, **kwargs):
        self.__dict__.update((key, None) for key in Traits.ALLOWED_KEYS)
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in Traits.ALLOWED_KEYS)

    @classmethod
    def merge(cls, child, self_traits, default_traits):
        merged_traits = Traits()
        for key in Traits.ALLOWED_KEYS:
            if hasattr(child, 'traits') and child.traits and getattr(child.traits, key, None) is not None:
                setattr(merged_traits, key, getattr(child.traits, key))
            elif self_traits and getattr(self_traits, key, None) is not None:
                setattr(merged_traits, key, getattr(self_traits, key))
            elif default_traits and getattr(default_traits, key, None) is not None:
                setattr(merged_traits, key, getattr(default_traits, key))
        return merged_traits

