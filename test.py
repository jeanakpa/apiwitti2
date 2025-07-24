from Models.mywitti_survey import MyWittiSurvey, MyWittiSurveyOption
from extensions import db

# Insérer le sondage (si absent)
if not MyWittiSurvey.query.get(3):
    survey = MyWittiSurvey(id=3, title="Test Survey 3", description="Un sondage de test pour vérifier les réponses", is_active=True)
    db.session.add(survey)
    db.session.commit()

# Insérer les options (si absentes)
if not MyWittiSurveyOption.query.filter_by(survey_id=3).first():
    options = [
        MyWittiSurveyOption(survey_id=3, option_text="Très mal", option_value=1),
        MyWittiSurveyOption(survey_id=3, option_text="Mal", option_value=2),
        MyWittiSurveyOption(survey_id=3, option_text="Moyen", option_value=3),
        MyWittiSurveyOption(survey_id=3, option_text="Bien", option_value=4),
        MyWittiSurveyOption(survey_id=3, option_text="Très bien", option_value=5)
    ]
    db.session.add_all(options)
    db.session.commit()

print("Sondage 3 et options insérés :", MyWittiSurvey.query.get(3), [opt.id for opt in MyWittiSurveyOption.query.filter_by(survey_id=3).all()])