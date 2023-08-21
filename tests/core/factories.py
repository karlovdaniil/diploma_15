import factory


class SingUpRequest(factory.DictFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')
    password_repeat = factory.LazyAttribute(lambda o: o.password)


class LoginRequest(factory.DictFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')


class UpdatePasswordRequest(factory.DictFactory):
    old_password = factory.Faker('password')
    new_password = factory.Faker('password')
