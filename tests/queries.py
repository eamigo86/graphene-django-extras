ALL_USERS = """query {
  allUsers {
    results {
      id
    }
  }
}
"""
ALL_USERS1 = """query {
  allUsers1 {
      id
      username
      firstName
      lastName
      email
  }
}
"""
ALL_USERS2 = """query {
  allUsers2 {
      username
  }
}
"""
ALL_USERS3 = """query {
  allUsers3 {
      id
  }
}
"""
ALL_USERS3_WITH_FILTER = """query {
  allUsers3 (%(filter)s) {
    results {
      %(fields)s
    }
  }
}
"""

# Queries for DjangoSerializerType
USER = """query {
  user2 (%(filter)s) {
      %(fields)s
  }
}
"""

USERS = """query {
  users(%(filter)s){
    results(%(pagination)s){
        %(fields)s
    },
    totalCount
  }
}
"""

generic_query = """
query{
    %(name)s(%(params)s){
        %(fields)s
    }
}
"""
create_mutation = """
    mutation %(name)s($text: String!){
        %(name)s(text: $text){
            ok
        }
    }
"""

update_mutation = """
    mutation %(name)s($id: ID!, $text: String!){
        %(name)s(id: $id, text: $text){
            ok
        }
    }
"""

delete_mutation = """
    mutation %(name)s($id: ID!){
        %(name)s(id: $id){
            ok
        }
    }
"""

