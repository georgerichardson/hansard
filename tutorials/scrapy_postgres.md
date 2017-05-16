# Scrapy + PostgreSQL: Scraping Relational Items from the Web

Scrapy is a powerful Python module for crawling websites and systematically collecting content to store in a format of the user's choosing. Sometimes it's convenient to write the results to disk in one or several files, such as text, csv, or json depending on the nature of the scraped information. However, in some cases you may want to capture multiple elements from a website that have connections to one another, and are more suited to being stored in a database. 

As an example, we're going to look at the website [velobase.com](http://velobase.com/), a catalogue of vintage bike components. Pretty handy if that's, er, your thing... Anyway, let's imagine we wanted to build our own database of the bike components listed on that site. *Components* are listed under *Component Groups*, which are in turn listed under *Brands*. We want to know the groupset and manufacturer information for every component we scrape, but we don't want to have to repeatedly store that data. It's going to be much more efficient to store tables of brands, component groups, and components and link them in a database. So let's have a look at how we can do this in Python.

## 1. Setting up the Database

For this example, I'm going to use PostgreSQL (also referred to as Postgres), but you can copy the rest of this guide using any SQL system you like. First up, head to the [PostgreSQL download page](https://www.postgresql.org/download/) and choose an installation path for your operating system (I used the [Postgres App](http://postgresapp.com/)). If you are on windows, the easiest way to get up and running is with EnterpriseDB.

To start the Postgres client For Mac or Linux, open a terminal window or tab and type:

~~~ bash
$ psql -h locahost -d postgres
~~~

Windows users should follow the instructions [here](https://www.enterprisedb.com/resources/tutorials/getting-started-edb-postgres%E2%84%A2-advanced-server-windows%C2%AE) under “Starting the SQL Command Line Terminal”.

This will return

~~~ bash
psql (9.1.4, server 9.1.3)
Type "help" for help.

postgres=#
~~~

You're now in Postgres, as indicated by the `postgres=#` prompt, and can issue commands to create, modify and query anything to do with your databases. If running for the first time, your prompt might be your computer name followed by `=#`. If you want to create a user called *postgres*, simply use the command

~~~ bash
postgres=# CREATE USER postgres;
~~~

Note the semicolon at the end, which tells Postgres that this is the end of a statement to execute.

Now create a database associated with the project

~~~ bash
postgres=# CREATE DATABASE velobase;
~~~

That's it! Finally, you just need to connect to the database in order to view the tables that we're going to make. The prompt will change to let you know that you're connected.

~~~ bash
postgres=#\c velobase postgres;
velobase=#
~~~

Now to set up Python.

## 2. Setting up a Project Environment

My preferred way to use Python is with Conda. Conda allows you to install Python packages, but more importantly it can create isolated Python installations on your system. These are referred to as environments, and mean that you can have many specific configurations of Python on your computer for different projects. On a basic level, this is useful for a number reasons:

1. It means that you can install the specific version of a package you might need for one project, while not affecting any others.
2. You can have separate environments for packages that may conflict with each other.
3. You can mess up a Conda environment and just delete it, rather than risk screwing up your system's native Python installation.

To install Conda just follow the appropriate steps from their website. Once you have it set up, you can check for environments on your system.

~~~ bash
$ conda env list
root *
~~~

Unless you've used Conda before, you should see only the root environment. Let's create one specifically for this project.

~~~ bash
$ conda create -n velobase_scraper python=3 scrapy sqlalchemy
~~~

This creates an environment with name (`-n`) *velobase_scraper*, using the latest version of Python 3, and with Scrapy and sqlalchemy preinstalled. Now activate it, and you should be greeted by a new prompt telling you that you're using the environment.

~~~ bash
$ source activate velobase_scraper
(velobase_scraper) $
~~~

Let's start our Scrapy project!

## 3. Setting up Scrapy

First create a folder for the project. I like to put things in my `projects` folder.

~~~ bash
(velobase_scraper) $ mkdir ~/projects/velobase_scraper
(velobase_scraper) $ cd ~/projects/velobase_scraper
~~~
