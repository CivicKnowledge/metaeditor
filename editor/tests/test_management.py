# -*- coding: utf-8 -*-
import os
import csv

import fudge

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from compat.tests.helpers import patch_identifier_index, restore_patched

from editor.models import Source, Category, Format
from editor.tests.factories import SourceFactory, CategoryFactory, FormatFactory


class LoadSourcesTest(TestCase):

    @classmethod
    def setUpClass(cls):

        # cache sources.csv rows for all tests
        sources = os.path.join(
            settings.BASE_DIR, '../', 'editor', 'data', 'sources.csv')

        cls._csv_rows = []
        with open(sources) as csvfile:
            reader = csv.DictReader(csvfile)
            for node in reader:
                cls._csv_rows.append(node)

        cls._csv_id_to_name_map = {}
        for row in cls._csv_rows:
            cls._csv_id_to_name_map[row['id']] = row['name']

    def test_raises_command_error_if_sources_exist(self):
        SourceFactory()
        self.assertRaises(CommandError, call_command, 'load_sources', verbosity=0)

    def _assert_all_nodes_imported(self):
        missed = []
        for row in self._csv_rows:
            qs = Source.objects.filter(name=row['name'])
            if not qs.exists():
                missed.append(row['name'])

        self.assertFalse(bool(missed), '%s missed' % missed)

        self.assertEqual(
            Source.objects.all().count(),
            len(self._csv_rows))

        for node in self._csv_rows:
            node_instance = Source.objects.get(
                name=node['name'],
                abbreviation=node['abbreviation'],
                domain=node['domain'],
                homepage=node['homepage'],
                about=node['about'])

            if node['parent_id']:
                self.assertEquals(
                    node_instance.parent.name,
                    self._csv_id_to_name_map[node['parent_id']])
            else:
                # root node
                self.assertIsNone(node_instance.parent)

    def test_deletes_existing_and_creates_new_nodes(self):
        s1 = SourceFactory()
        s2 = SourceFactory()
        self.assertEqual(Source.objects.all().count(), 2)
        call_command('load_sources', verbosity=0, delete=True)
        self.assertEquals(Source.objects.filter(name=s1.name).count(), 0)
        self.assertEquals(Source.objects.filter(name=s2.name).count(), 0)
        self._assert_all_nodes_imported()

    def test_saves_all_nodes(self):
        self.assertEqual(Source.objects.all().count(), 0)
        call_command('load_sources', verbosity=0)
        self._assert_all_nodes_imported()


class CreateRootsTest(TestCase):

    def _assert_creates_root(self, model_class):
        call_command('create_roots', verbosity=0)
        qs = model_class.objects.filter(name='!ROOT!')
        self.assertEquals(qs.count(), 1)
        self.assertIsNone(qs[0].parent)

    def _assert_changes_existing_roots(self, model_class):
        if model_class == Source:
            model_factory = SourceFactory
        elif model_class == Category:
            model_factory = CategoryFactory
        elif model_class == Format:
            model_factory = FormatFactory
        else:
            raise Exception('Do not know the factory of the %s model' % model_class)

        # create some root instances
        instance1 = model_factory(parent=None)
        instance2 = model_factory(parent=None)
        instance3 = model_factory(parent=None)

        assert model_class.objects.filter(parent__isnull=True).count(), 3
        call_command('create_roots', verbosity=0)

        # now testing
        qs = model_class.objects.filter(parent__isnull=True)
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs[0].name, '!ROOT!')

        # all old roots moved to new root children
        self.assertIsNotNone(model_class.objects.get(id=instance1.id).parent)
        self.assertEquals(
            model_class.objects.get(id=instance1.id).parent.name,
            '!ROOT!')

        self.assertIsNotNone(model_class.objects.get(id=instance2.id).parent)
        self.assertEquals(
            model_class.objects.get(id=instance2.id).parent.name,
            '!ROOT!')

        self.assertIsNotNone(model_class.objects.get(id=instance3.id).parent)
        self.assertEquals(
            model_class.objects.get(id=instance3.id).parent.name,
            '!ROOT!')

    def test_creates_source_root(self):
        self._assert_creates_root(Source)

    def test_creates_format_root(self):
        self._assert_creates_root(Format)

    def test_creates_category_root(self):
        self._assert_creates_root(Category)

    def test_changes_existing_source_roots(self):
        self._assert_changes_existing_roots(Source)

    def test_changes_existing_category_roots(self):
        self._assert_changes_existing_roots(Category)

    def test_changes_existing_format_roots(self):
        self._assert_changes_existing_roots(Format)

    def test_does_not_create_source_root_twice(self):
        call_command('create_roots', verbosity=0)
        qs = Source.objects.filter(name='!ROOT!')
        self.assertEquals(qs.count(), 1)
        self.assertIsNone(qs[0].parent)

        call_command('create_roots', verbosity=0)
        qs = Source.objects.filter(name='!ROOT!')
        self.assertEquals(qs.count(), 1)
        self.assertIsNone(qs[0].parent)


class SetupAmbrySearchTest(TestCase):

    # helpers
    def _patch_identifier_index(self, result):
        """ Patches ambry search identifier to return given result. """
        patch_identifier_index(result)

    def _restore_patched(self):
        restore_patched()

    @fudge.patch('ambry._meta')
    def test_raises_commanderror_if_old_version_of_ambry_found(self, fake_meta):
        fake_meta.has_attr(__version__='0.3.704')
        try:
            call_command('setup_ambry_search', verbosity=0)
        except CommandError as exc:
            self.assertIn('ambry >= 0.3.705', exc.message)

    @fudge.patch(
        'ambry._meta',
        'editor.management.commands.setup_ambry_search.call')
    def test_sets_up_search_system(self, fake_meta, fake_call):
        fake_meta.has_attr(__version__='0.3.705')
        fake_call.expects_call()\
            .with_args(['ambry', 'config', 'install'])\
            .next_call()\
            .with_args(['ambry', 'sync'])\
            .next_call()\
            .with_args(['ambry', 'search', '-R'])
        call_command('setup_ambry_search', verbosity=0)

    @fudge.patch(
        'ambry._meta',
        'editor.management.commands.setup_ambry_search.call')
    def test_raises_exception_if_search_failed(self, fake_meta, fake_call):
        fake_meta.has_attr(__version__='0.3.705')
        fake_call.expects_call()

        # fudge failed to patch methods from library package because
        # of ambry/__init__.py/library function. That is why I patch it here.
        search_result = []
        self._patch_identifier_index(search_result)
        try:
            call_command('setup_ambry_search', verbosity=0)
        except CommandError as exc:
            self.assertIn('I couldn\'t find California term', exc.message)
        finally:
            self._restore_patched()
