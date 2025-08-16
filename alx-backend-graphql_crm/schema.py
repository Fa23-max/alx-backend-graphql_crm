import graphene
from crm.schema import Query as AppQuery, Mutation as AppMutation

class Query(AppQuery, graphene.ObjectType):
    pass

class Mutation(AppMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)