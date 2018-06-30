ALL_USERS = '''query {
  allUsers {
    results {
      id
    }
  }
}
'''
ALL_USERS1 = '''query {
  allUsers1 {
      id
  }
}
'''
ALL_USERS2 = '''query {
  allUsers2 {
      id
  }
}
'''
ALL_USERS3 = '''query {
  allUsers3 {
      id
  }
}
'''
ALL_USERS3_WITH_FILTER = '''query {
  allUsers3 (%(filter)s) {
    results {
      %(fields)s
    }
  }
}
'''
