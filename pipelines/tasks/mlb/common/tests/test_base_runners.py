from ..helpers.parsers import BaseRunners


def test_pickoff_error_1():
    current_bases_state = [1, 0, 0]
    entities = {
      "player": "Gray",
      "type": "pickoff error",
      "moves": [
        {
          "player": "Straw",
          "type": "advanced",
          "at": "second",
          "how": "pickoff error",
          "by": "Gray"
        },
        {
          "player": "Straw",
          "type": "advanced",
          "at": "third",
          "how": "fielding error",
          "by": "Wallner"
        }
      ]
    }

    bases = BaseRunners().play(entities, current_bases_state)
    assert bases == [0, 0, 1]

def test_pickoff_error_1():
    current_bases_state = [1, 1, 0]
    entities = {
      "player": "Severino",
      "type": "pickoff error",
      "moves": [
        {
          "player": "Kiermaier",
          "type": "advanced",
          "at": "second"
        },
        {
          "player": "Margot",
          "type": "advanced",
          "at": "third",
          "how": "pickoff error",
          "by": "Severino"
        }
      ]
    }

    bases = BaseRunners().play(entities, current_bases_state)
    assert bases == [0, 1, 1]

def test_pickoff_error_2():
    current_bases_state = [1, 1, 0]
    entities = {
      "player": "Severino",
      "type": "pickoff error",
      "moves": [
        {
          "player": "Margot",
          "type": "advanced",
          "at": "home",
          "how": "pickoff error",
          "by": "Severino"
        },
        {
          "player": "Kiermaier",
          "type": "advanced",
          "at": "second"
        },
      ]
    }

    bases = BaseRunners().play(entities, current_bases_state)
    assert bases == [0, 1, 0]
