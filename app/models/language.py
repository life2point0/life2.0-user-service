from .id_name_pair import create_id_name_pair_model
from .base import TimeStampedModel
from .association_tables import get_user_association_table
from sqlalchemy.orm import relationship

table_name = 'languages'
singular_name = 'language'

IDNamePairModel = create_id_name_pair_model(table_name)

user_languages_table = get_user_association_table(table_name, f'{singular_name}_id')

class LanguageModel(IDNamePairModel, TimeStampedModel):
    users = relationship('UserModel', secondary=user_languages_table, back_populates=table_name)
