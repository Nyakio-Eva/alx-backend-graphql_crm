import graphene
from crm.schema import Query as CrmQuery, Mutation as CrmMutation

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

schema = graphene.Schema(query=Query)
class Query(CrmQuery, graphene.ObjectType):
    pass

class Mutation(CrmMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)