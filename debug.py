#!/usr/bin/env python3

from sqlalchemy import create_engine

from lib.sqlalchemy_sandbox import Student

engine = create_engine('sqlite:///db/students.db')
import ipdb; ipdb.set_trace()
