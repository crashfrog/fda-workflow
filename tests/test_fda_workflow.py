#!/usr/bin/env python

"""Tests for `fda_workflow` package."""


import unittest

from fda_workflow import FdaRunJob
from tests import runs, paths, jobs
from hypothesis import given

from porerefiner import models

from peewee import SqliteDatabase


class TestFda_workflow(unittest.TestCase):
    """Tests for `fda_workflow` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.db = db = SqliteDatabase(":memory:", pragmas={'foreign_keys':1}, autoconnect=False)
        db.bind(models.REGISTRY, bind_refs=False, bind_backrefs=False)
        db.connect()
        db.create_tables(models.REGISTRY)

    def tearDown(self):
        """Tear down test fixtures, if any."""
        db = self.db
        db.drop_tables(models.REGISTRY)
        db.close()

    @given(
        jobs(subclass_of=FdaRunJob, classdef={}),
        runs(),
        paths(real=True),
        paths(pathlib_only=True)
    )
    def test_000_something(self, job, run, datadir, remotedir):
        """Test something."""
        self.assertIsNotNone(job.setup(run, datadir, remotedir))
