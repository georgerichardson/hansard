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
    print("Checking if party exists")
    if session.query(exists().where(Party.party==party.party)).scalar():
        print("It does")
        party = session.query(Party).filter_by(party=party.party).first()
        return party
    else:
        return party

def check_existing_mp(mp, session):
    print("Checking if MP exists")
    if session.query(exists().where(MP.name==mp.name)).scalar():
        print("They do")
        mp = session.query(MP).filter_by(name=mp.name).first()
        return mp
    else:
        return mp

def check_existing_debate(debate, session):
    print("Checking if debate exists")
    if session.query(exists().where(Debate.debate_identifier==debate.debate_identifier)).scalar():
        print("It does")
        debate = session.query(Debate).filter_by(debate_identifier=debate.debate_identifier).first()
        return debate
    else:
        return debate

def get_member_by_id(member_identifier, session):
    print("Fetching member by ID")
    if session.query(exists().where(MP.member_identifier==str(member_identifier))).scalar():
        member =  session.query(MP).filter_by(member_identifier=str(member_identifier)).first()
        return member
    else:
        return None

class HansardPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine, autoflush=False)

    def process_item(self, item, spider):
        session = self.Session()
        
        try:
            if type(item) is hansard.items.Member:
                print("Attempting to add MP")
                party = item['party']
                party = Party(**party)

                party = check_existing_party(party, session)

                mp = MP(name=item['name'], 
                           start_year=item['start_year'],
                           end_year=item['end_year'],
                           constituency_last=item['constituency_last'],
                           house=item['house'],
                           party=party,
                           member_identifier=item['member_identifier'],
                           member_url=item['member_url']
                           )
                name = mp.name

                #import pdb; pdb.set_trace()
                if session.query(exists().where(MP.member_identifier==str(mp.member_identifier))).scalar():
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
                #import pdb; pdb.set_trace()
                member_identifier = item['member_identifier']
                member = get_member_by_id(member_identifier, session)
                item['member'] = member
                #mp = MP(name=mp['name'])
                #mp = check_existing_mp(mp, session)
                #item['mp'] = mp

                debate = item['debate']
                debate = Debate(**debate)
                debate = check_existing_debate(debate, session)
                item['debate'] = debate

                spoken_contribution = SpokenContribution(**item)
                if session.query(exists().where(SpokenContribution.contribution_identifier==spoken_contribution.contribution_identifier)).scalar():
                    session.close()
                else:
                    #import pdb; pdb.set_trace()
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
                if session.query(exists().where(Debate.debate_identifier==debate.debate_identifier)).scalar():
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