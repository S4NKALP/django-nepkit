"""
Tests for django-nepkit language utilities (lang_utils.py).
"""


class TestResolveLanguageParams:
    """Tests for resolve_language_params()."""

    def test_defaults_to_english(self):
        """With no args and default settings (en), ne=False and en=True."""
        from django_nepkit.lang_utils import resolve_language_params

        ne, en = resolve_language_params()
        assert ne is False
        assert en is True

    def test_ne_true_sets_en_false(self):
        """When ne=True is explicitly passed, en should be False."""
        from django_nepkit.lang_utils import resolve_language_params

        ne, en = resolve_language_params(ne=True)
        assert ne is True
        assert en is False

    def test_en_true_sets_ne_false(self):
        """When en=True is explicitly passed, ne should be False."""
        from django_nepkit.lang_utils import resolve_language_params

        ne, en = resolve_language_params(en=True)
        assert ne is False
        assert en is True

    def test_explicit_en_true_with_ne_true(self):
        """When both ne=True and en=True, en should respect the explicit value."""
        from django_nepkit.lang_utils import resolve_language_params

        ne, en = resolve_language_params(ne=True, en=True)
        # ne=True with explicit en=True — en is explicitly set, so it stays True
        assert ne is True
        assert en is True

    def test_ne_false_sets_en_true(self):
        """When ne=False is explicitly passed, en should be True."""
        from django_nepkit.lang_utils import resolve_language_params

        ne, en = resolve_language_params(ne=False)
        assert ne is False
        assert en is True

    def test_via_kwargs_ne(self):
        """ne can be passed via **kwargs."""
        from django_nepkit.lang_utils import resolve_language_params

        ne, en = resolve_language_params(**{"ne": True})
        assert ne is True
        assert en is False

    def test_via_kwargs_en(self):
        """en can be passed via **kwargs."""
        from django_nepkit.lang_utils import resolve_language_params

        ne, en = resolve_language_params(**{"en": True})
        assert ne is False
        assert en is True


class TestPopLanguageParams:
    """Tests for pop_language_params()."""

    def test_pops_ne_from_kwargs(self):
        """ne is consumed from the kwargs dict."""
        from django_nepkit.lang_utils import pop_language_params

        kwargs = {"ne": True, "other": "value"}
        ne, en = pop_language_params(kwargs)

        assert ne is True
        assert en is False
        assert "ne" not in kwargs  # was popped
        assert "other" in kwargs  # unrelated keys remain

    def test_pops_en_from_kwargs(self):
        """en is consumed from the kwargs dict."""
        from django_nepkit.lang_utils import pop_language_params

        kwargs = {"en": True, "other": "value"}
        ne, en = pop_language_params(kwargs)

        assert en is True
        assert ne is False
        assert "en" not in kwargs  # was popped

    def test_defaults_when_nothing_set(self):
        """Without any language kwargs, defaults from settings are used."""
        from django_nepkit.lang_utils import pop_language_params

        kwargs = {}
        ne, en = pop_language_params(kwargs)

        # Default language is 'en' in test settings
        assert ne is False
        assert en is True

    def test_ne_true_en_not_explicit(self):
        """When ne=True is in kwargs and en is absent, en becomes False."""
        from django_nepkit.lang_utils import pop_language_params

        kwargs = {"ne": True}
        ne, en = pop_language_params(kwargs)

        assert ne is True
        assert en is False

    def test_ne_true_en_explicit_true(self):
        """When both ne=True and en=True are in kwargs, en respects the explicit value."""
        from django_nepkit.lang_utils import pop_language_params

        kwargs = {"ne": True, "en": True}
        ne, en = pop_language_params(kwargs)

        assert ne is True
        assert en is True

    def test_extra_kwargs_not_touched(self):
        """Other kwargs are left intact after popping language params."""
        from django_nepkit.lang_utils import pop_language_params

        kwargs = {"ne": False, "max_length": 100, "blank": True}
        pop_language_params(kwargs)

        assert "max_length" in kwargs
        assert "blank" in kwargs
