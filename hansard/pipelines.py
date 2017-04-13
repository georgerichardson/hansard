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
        self.Session = sessionmaker(bind=engine, autoflush=False)

    def process_item(self, item, spider):
        session = self.Session()
        

        try:
            if type(item) is hansard.items.MP:
                print("Attempting to add MP")
                #import pdb; pdb.set_trace()
                #mp = MP(**item)
                party = item['party']
                party = Party(**party)

                if session.query(exists().where(Party.party==party.party)).scalar():
                    print("Party already in DB")
                    party = session.query(Party).filter_by(party=party.party).first()

                mp = MP(name=item['name'], 
                           start_year=item['start_year'],
                           end_year=item['end_year'],
                           constituency_last=item['constituency_last'],
                           house=item['house'],
                           party=party
                           )
                name = mp.name
                #import pdb; pdb.set_trace()
                if session.query(exists().where(MP.name==name)).scalar():
                    print("MP already exists")
                    session.close()
                else:
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
                print("Attempting to add Party")
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