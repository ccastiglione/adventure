import random


class Result:

    def __init__(self, message, success=None):
        self.messages = [message]
        self.success = success

    def __str__(self):
        return self.messages[0]

    def __eq__(self, other):
        if isinstance(other, Result):
            return (self.success == other.success
                    and self.messages == other.messages)
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

    def append(self, message, index=0):
        self.messages[index] += message

    def add_message(self, message):
        self.messages.append(message)

    def get_message(self):
        index = random.randint(0, len(self.messages) - 1)
        return self.messages[index]

    def set_message(self, value):
        self.messages[0] = value

    message = property(get_message, set_message)


class Success(Result):

    def __init__(self, message):
        super(Success, self).__init__(message, success=True)


class Failure(Result):

    def __init__(self, message):
        super(Failure, self).__init__(message, success=False)


class OwnershipFailure(Failure):

    def __init__(self, item_name, article='the'):
        super(OwnershipFailure, self).__init__("You don't have {} {}!".format(article, item_name))


class ProximityFailure(Failure):

    def __init__(self, item_name):
        super(ProximityFailure, self).__init__("I don't see any {} here".format(item_name))


class NotUnderstoodFailure(Failure):

    def __init__(self, invalid_word=None):
        if invalid_word:
            message = "Sorry, I don't know what you mean by '{}'".format(invalid_word)
        else:
            message = "Sorry, I didn't understand that"
        super(NotUnderstoodFailure, self).__init__(message)


class AmbiguousNounFailure(Failure):
    def __init__(self, matches):
        matched_list = list(matches)
        if len(matched_list) == 2:
            message = "Which do you mean, the {} or the {}?"\
                .format(matched_list[0].full_name(), matched_list[1].full_name())
        else:
            message = "Which do you mean: "
            for m in matched_list[:-1]:
                message += "\n\tthe {},".format(m.full_name())
            message += "\n\tor the {}?".format(matched_list[-1].full_name())
        super(AmbiguousNounFailure, self).__init__(message)


GENERIC_SUCCESS = Success("Success")
GENERIC_FAILURE = Failure("Failure")
