import legume
class TestPos(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+1
    MessageValues = {
        'name' : 'string 128',
        'x' : 'int',
        'y' : 'int',
        }

legume.messages.message_factory.add(TestPos)

