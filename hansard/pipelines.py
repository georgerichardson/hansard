# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from hansard.models import MP, Debate, SpokenContribution, Party, db_connect, create_table
import hansard.items

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class HansardPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        print("Attempting to add to DB")

        try:
            if type(item) is hansard.items.MP:
                mp = MP(**item)
                try:
                    session.add(mp)
                    session.commit()
                    print("Sucess!!")
                except:
                    session.rollback()
                    print("Failure...")
                finally:
                    session.close()
                    print("All done")
        except:
            raise
        return item