# Working with Seed Data

## Learning Goals

- Use an external library to simplify tasks from ORM and Advanced ORM.
- Manage database tables and schemas without ever writing SQL through Alembic.
- Use SQLAlchemy to create, read, update and delete records in a SQL database.

***

## Key Vocab

- **Persist**: save a schema in a database.
- **Migration**: the process of moving data from one or more databases to one
  or more target databases.
- **Seed**: to fill a database with an initial set of data.

***

## Introduction

What good is a database without any data? When working with any application
involving a database, it's a good idea to populate your database with some
realistic data when you are working on building new features. SQLAlchemy, and
many other ORMs, refer to the process of adding sample data to the database as
**"seeding"** the database. In this lesson, we'll see some of the conventions
and built-in features that make it easy to seed data in an SQLAlchemy
application.

This lesson is set up as a code-along, so make sure to fork and clone the
lesson. Then run these commands to set up the dependencies and set up the
database:

```console
$ pipenv install
# => Installing dependencies from Pipfile.lock (xxxxxx)...
# =>   🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ X/X — XX:XX:XX
# => To activate this project's virtualenv, run pipenv shell.
# => Alternatively, run a command inside the virtualenv with pipenv run.
$ pipenv shell
# => Launching subshell in virtual environment...
# =>  . /python-p3-working-with-seed-data/.venv/bin/activate
# => $  . /python-p3-working-with-seed-data/.venv/bin/activate
$ cd seed_db && alembic upgrade head
```

In this application, we have two migrations: one for our declarative `Base`,
and a second for a table called `games`.

```py
# app//db.py

class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer(), primary_key=True)
    title = Column(String())
    genre = Column(String())
    platform = Column(String())
    price = Column(Integer())
    created_at = Column(DateTime(), server_default=func.now())
    updated_at = Column(DateTime(), onupdate=func.now())

```

***

## Why Do We Need Seed Data?

With SQLAlchemy, we've seen how simple it is to add data to a database by
using built-in methods that will write SQL code for us. For instance, to create
a new record in the `games` table, you can open up the Python shell, generate
a SQLAlchemy session, create an instance of the `Game` model, and commit it to
the session. To simplify this even further, we've used `app/debug.py` to create
a session and `import` relevant classes. Run `debug.py` from the `seed_db` and
directory and enter the following into the `ipdb` shell:

```py
botw = Game(title="Breath of the Wild", platform="Switch", genre="Adventure", price=60)
session.add(botw)
session.commit()
```

Awesome! Our database now has some data in it. We can create a few more games:

```py
ffvii = Game(title="Final Fantasy VII", platform="Playstation", genre="RPG", price=30)
mk8 = Game(title="Mario Kart 8", platform="Switch", genre="Racing", price=50)
session.bulk_save_objects([ffvii, mk8])
session.commit()
```

Since these records are saved in the database rather than in Python's memory, we
know that even after we exit the `ipdb` shell, we'll still be able to retrieve
this data.

But how can we share this data with other developers who are working on the same
application? How could we recover this data if our development database was
deleted? We could include the database in version control, but this is generally
considered bad practice: since our database might get quite large over time,
it's not practical to include it in version control (you'll even notice that in
our SQLAlchemy projects' `.gitignore` file, we include a line that instructs
Git not to track any `.sqlite3` files). There's got to be a better way!

The common approach to this problem is that instead of sharing the actual
database with other developers, we share the **instructions for creating data in
the database** with other developers. By convention, the way we do this is by
creating a Python file, `app/seed.py`, which is used to populate our database.

We've already seen a similar scenario by which we can share instructions for
setting up a database with other developers: using SQLAlchemy migrations to
define how the database tables should look. Now, we'll have two kinds of database
instructions we can use:

- Migrations: define how our tables should be set up.
- Seeds: add data to those tables.

***

## Defining Tables via SQLAlchemy ORM

Creating tables with SQLAlchemy ORM requires classes with four key traits:

1. Inheritance from a `declarative_base` object.
2. A `__tablename__` class attribute.
3. One or more `Column`s as class attributes.
4. A `Column` specified to be the table's primary key.

Let's take a look at a class to define a `students` table:

```py
# sqlalchemy_sandbox.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    student_id = Column(Integer(), primary_key=True)
    student_name = Column(String())
```

The `declarative_base` combines a container for table metadata as well as a
group of methods that act as mappers between Python and our SQL database.
Inheritance from `Base`, a `declarative_base` object, allows us to avoid
rewriting code.

<details>
  <summary>
    <em>Is <code>Base</code> a parent or child object?</em>
  </summary>

  <h3>A parent.</h3>
  <p>Just as in real life, children in Python inherit from their parents.</p>
</details>
<br/>

The `__tablename__` attribute will eventually be used as the name of our SQL
database table. The table's columns are identified using `Column` objects as
attributes- the optional `primary_key` argument tells SQLAlchemy that
`student_id` will be the primary key for the `students` table.

This type of class is called a **data model**, or **model**.

## Persisting the Schema

We have all of the data we need to generate a database table, but it won't
happen as soon as we save our module. We need to execute a series of Python
statements to do **persist** our schema. You can do this from the Python shell,
but we will be using a script for this exercise.

```py
#!/usr/bin/env python3

# imports
from sqlalchemy import create_engine

# data models

engine = create_engine('sqlite:///db/students.db')
Base.metadata.create_all(engine)
```

Now run `chmod +x lib/sqlalchemy_sandbox.py` to make the script executable.
Run `lib/sqlalchemy_sandbox.py` from your Pipenv shell and you should see that
a `students.db` has popped up in the `db` directory with a `students` table.

Just as with using the `sqlite3` Python module on its own, we need to start by
creating a connection to the database. The engine is "home base" for the
database- everything on the database side and the Python side must pass through
the engine for the process to count. Here, we're pointing to a local sqlite
file where our tables will be created.

The `create_all()` command on the next line tells the engine that any models
that were created using `Base` as a parent should be used to create tables. if
you open `students.db` in VSCode, you should see that a table exists with two
columns: `student_id` and `student_name`.

### Improving our Script

While inclusion of the shebang is enough to tell the interpreter that a module
should be interpreted as a script, this presents a conundrum for larger
projects: _how does this affect `import` statements?_

As it turns out, the interpreter gets a bit confused when an `import` statement
encounters a script. As written above, `Base.metadata.create_all(engine)` would
be run before the code of any module that imported `sqlalchemy_sandbox.py`.
There's a trick to avoid this:

```py
if __name__ == '__main__':
    engine = create_engine('sqlite:///db/students.db')
    Base.metadata.create_all(engine)
```

`__name__` is an attribute possessed by modules that is assigned at runtime. It
is assigned the value `'__main__'` if the module is the main program; that is,
the one that you called from the command line.

Refactoring any scripted elements of our modules to fit into this block makes
sure that the script only runs when we tell it to.

***

## Conclusion

You should know now how to define and persist a simple schema using SQLAlchemy.
In the next lesson, we will explore how to create, read, update, and delete
records with SQLAlchemy ORM.

***

## Resources

- [SQLAlchemy ORM Documentation][sqlaorm]
- [6. Defining Schema with SQLAlchemy ORM - O'Reilly](https://learning.oreilly.com/library/view/essential-sqlalchemy-2nd/9781491916544/ch06.html)

[sqla]: https://www.sqlalchemy.org/
[sqlacore]: https://docs.sqlalchemy.org/en/14/core/
[sqlaorm]: https://docs.sqlalchemy.org/en/14/orm/
