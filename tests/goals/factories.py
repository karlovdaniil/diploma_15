import factory


class CreateGoalRequest(factory.DictFactory):
    title = factory.Faker('catch_phrase')
