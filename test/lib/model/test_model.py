# import os
# import unittest
# from lib.model.model import Model
# from lib import schemas
#
# class TestModel(unittest.TestCase):
#     def test_respond(self):
#         model = Model()
#         self.assertEqual(model.respond(schemas.parse_message({"body": schemas.GenericItem(id='123', callback_url="http://example.com/callback", text="hello")})), model.respond(schemas.parse_message({"body": schemas.GenericItem(id='123', callback_url="http://example.com/callback", text="hello"), "response": []})))
#
# if __name__ == '__main__':
#     unittest.main()