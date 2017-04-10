# -*- coding: utf-8 -*-

from sqlalchemy import exists
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
                if session.query(exists().where(MP.name==mp.name)).scalar():
                    session.close()
                else:
                    #party = Party(**mp.party)
                    #mp.party = party
                    try:
                        session.add(mp)
                        session.commit()
                        print("MP added")
                    except:
                        session.rollback()
                        print("Failed to add MP")
                    finally:
                        session.close()
                        print("All done")

            elif type(item) is hansard.items.Party:
                party = Party(**item)
                if session.query(exists().where(Party.party==party.party)).scalar():
                    session.close()
                else:
                    try:
                        session.add(party)
                        session.commit()
                        print("Party added")
                    except:
                        session.rollback()
                        print("Failed to add party")
                    finally:
                        session.close()
                        print("All done")

            elif type(item) is hansard.items.SpokenContribution:
                spoken_contribution = SpokenContribution(**item)
                if session.query(exists().where(SpokenContribution.contribution_id==spoken_contribution.contribution_id)):
                    session.close()
                else:
                    try:
                        session.add(spoken_contribution)
                        session.commit()
                        print("Spoken contribution added")
                    except:
                        session.rollback()
                        print("Failed to add spoken contribution")
                    finally:
                        session.close()
                        print("All done")

            elif type(item) is hansard.items.Debate:
                debate = Debate(**item)
                if session.query(exists().where(Debate.debate_id==debate.debate_id)):
                    session.close()
                else:
                    session.close()

        except:
            raise
        return item