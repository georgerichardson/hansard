# -*- coding: utf-8 -*-

from sqlalchemy import exists
from sqlalchemy.orm import sessionmaker
from hansard.models import MP, Debate, SpokenContribution, Party, db_connect, create_table
import hansard.items

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

def check_existing_party(party, session):
    if session.query(exists().where(Party.party==party.party)).scalar():
        print("Party already in DB")
        party = session.query(Party).filter_by(party=party.party).first()
        return party
    else:
        return party

def check_existing_mp(mp, session):
    if session.query(exists().where(MP.name==mp.name)).scalar():
        print("MP already in DB")
        mp = session.query(MP).filter_by(name=mp.name).first()
        return mp
    else:
        return mp

def check_existing_debate(debate, session):
    if session.query(exists().where(Debate.debate_id==debate.debate_id)).scalar():
        print("MP already in DB")
        debate = session.query(Debate).filter_by(debate_id=debate_id.debate_id).first()
        return debate
    else:
        return debate

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

                party = check_existing_party(party, session)

                mp = MP(name=item['name'], 
                           start_year=item['start_year'],
                           end_year=item['end_year'],
                           constituency_last=item['constituency_last'],
                           house=item['house'],
                           party=party
                           )
                name = mp.name
                self.mp = mp
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
                print("Attempting to add Spoken Contribution")
                import pdb; pdb.set_trace()
                mp = item['mp']
                mp = MP(name=mp['name'])
                mp = check_existing_mp(mp, session)
                item['mp'] = mp

                debate = item['debate']
                debate = Debate(**debate)
                debate = check_existing_debate(debate, session)
                item['debate'] = debate

                spoken_contribution = SpokenContribution(**item)
                

                if session.query(exists().where(SpokenContribution.contribution_id==spoken_contribution.contribution_id)).scalar():
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
                self.debate = debate
                if session.query(exists().where(Debate.debate_id==debate.debate_id)).scalar():
                    session.close()
                else:
                    try:
                        session.add(debate)
                        session.commit()
                        print("Debate added")
                    except:
                        session.rollback()
                        print("Failed to add debate")
                    finally:
                        session.close()
                        print("All done")
        except:
            raise
        return item