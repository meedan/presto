import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from lib.model.classycat import Model as ClassyCatModel
from lib import schemas
from lib.base_exception import PrestoBaseException
import json


class TestClassyCat(TestCase):
    def setUp(self):
        self.classycat_model = ClassyCatModel()

    @patch('lib.model.classycat_schema_create.upload_file_to_s3')
    @patch('lib.model.classycat_schema_create.file_exists_in_s3')
    def test_schema_create(self, file_exists_mock, upload_file_to_s3_mock):
        # should input a schema with more than one language and return an id
        # writing to s3 should be mocked
        # the format of the generated prompt should be checked

        upload_file_to_s3_mock.return_value = None
        file_exists_mock.return_value = False

        schema_input = {"model_name": "classycat__Model",
                        "body":
                            {"id": 1200,
                             "parameters": {
                                 "event_type": "schema_create",
                                 "schema_name": "2024 Indian Election Test",
                                 "topics": [
                                     {
                                         "topic": "Politics",
                                         "description": "This topic includes political claims, attacks on leaders and parties, and general political commentary."
                                     },
                                     {
                                         "topic": "Democracy & Election Integrity",
                                         "description": "This topic covers the integrity of the election process, including voter fraud, election fraud, the security of voting machines, and election interference, and electoral bonds."
                                     },
                                     {
                                         "topic": "Economy & Growth",
                                         "description": "This topic covers claims around economic growth, economic policies, GDP , employment, taxation, issues among farmer and manufacturing industry, and economic inequality."
                                     },
                                     {
                                         "topic": "Communalism",
                                         "description": "This topic covers attack on religious minorities, statements on religious freedom and polarization."
                                     },
                                     {
                                         "topic": "Education",
                                         "description": "This topic covers education policy of governments, educational institutions created, and quality of education in India."
                                     },
                                     {
                                         "topic": "Freedom of Expression",
                                         "description": "This topic covers claims regarding freedom of expression and  independence of media, and attacks on press freedom and journalists."
                                     },
                                     {
                                         "topic": "Foreign Policy",
                                         "description": "This topic covers India's relationship with neighbours and other countries, claims on effectiveness of foreign policy, international image and diplomacy."
                                     },
                                     {
                                         "topic": "Safety of Women",
                                         "description": "This topic covers the issue of safety of women and steps taken to prevent crimes against women. "
                                     },
                                     {
                                         "topic": "Social Issues",
                                         "description": "This topic covers topics on the citizenship ammendmend act and caste politics."
                                     },
                                     {
                                         "topic": "Health & Pharma",
                                         "description": "This topic covers health policies, claims on ayurveda, maternal and infant mortality, and the pharmaceutical industry."
                                     },
                                     {
                                         "topic": "Terrorism & National Security",
                                         "description": "This topics covers claims on UAPA, National security, Pakistan, and terrorism."
                                     },
                                     {
                                         "topic": "Corruption",
                                         "description": "This topic covers claims on corruptions and scams."
                                     },
                                     {
                                         "topic": "History",
                                         "description": "This topic covers claim on history of India and mythology."
                                     },
                                     {
                                         "topic": "Science & Technology",
                                         "description": "This topic covers claims on climate change, environment and science."
                                     },
                                     {
                                         "topic": "Banking & Finance",
                                         "description": "This topic covers claims around finance and banking."
                                     }
                                 ],
                                 "examples": [
                                     {
                                         "text": "Congress Manifesto is horrible. Never seen such a dangerous manifesto in my life. It's like vision 2047 document of PFI\n\nCheck these points of manifesto\n\n1. Will bring back triple talak (Muslim personal law)\n2. Reservation to Muslim in govt n private jobs (Implement Sachchar committee report)\n3. Support Love Jihad (right to love)\n4. Support Burqa in school (right to dress)\n5. End majoritarianism (Hinduism)\n6. Ban bulldozer action\n7. Support Gaza (Hamas)\n8. Legalise Same Sex Marriage, gender fluidity, trans movement\n9. Increase Muslim judges in judiciary\n10. Communal violence bill (will stop mob lynching)\n11. Legalise beef (right to eat everything)\n12. Separate loan intrest for Muslims\n13. Allow treason (No sedition)\n\nAll those Hindu who are thinking to vote Indi Alliance, NOTA or independent. Read this and think.\n",
                                         "labels": [
                                             "Politics",
                                             "Communalism"
                                         ]
                                     },
                                     {
                                         "text": "RSS ने अपने नागपुर मुख्यालय से 2024 लोकसभा चुनाव में कॉंग्रेस गठबंधन को समर्थन करने की घोषणा की कमाल की बात ये है कि इतनी महत्वपूर्ण खबर किसी भी news channel, और अखबार ने नहीं छापी RSS ने माना कि आज नरेंद्र मोदी भाजपा सरकार में देश का संविधान और लोकतंत्र खतरे में है इसलिए भाजपा को 2024 में रोकना अति आवश्यक है अगर देश की जनता धर्म के नशे में डूबी रही तो आने वाली नस्लें तुम्हें कभी माफ़ नहीं करेगी देश आज संकट में है और जो व्यक्ति इस समय कॉंग्रेस का साथ नहीं देगा वो भविष्य में खुद को कभी माफ़ नहीं कर पाएगा इस खबर को शेयर करके देश के एक जिम्मेदार नागरिक होने का फर्ज पूरा कीजिए",
                                         "labels": [
                                             "Politics",
                                             "Democracy & Election Integrity"
                                         ]
                                     },
                                     {
                                         "text": "बेहद गंभीर मामला है। खबरों के मुताबिक, दवा बनाने वाली बहुत सी कंपनियां जिनकी दवाएं टेस्ट में फेल हुईं, इन कंपनियों ने इलेक्टोरल बॉन्ड से चंदा दिया। जैसे \uD83D\uDC47 1. गुजरात की कंपनी 'टोरेंट फार्मास्यूटिकल' की बनाई 3 दवाएं ड्रग टेस्ट में फेल हुईं। इस कंपनी ने BJP को 61 करोड़ का चंदा दिया। 2. सिप्ला लिमिटेड कंपनी की बनाई दवाओं के 7 बार ड्रग टेस्ट फ़ेल हुए। इस कंपनी ने BJP को 37 करोड़ का चंदा दिया। 3. सन फ़ार्मा कंपनी की बनाई गई दवाओं के 6 बार ड्रग टेस्ट फ़ेल हुए। सन फार्मा ने BJP को 31.5 करोड़ रुपए का चंदा दिया। 4. गुजरात की कंपनी इंटास फ़ार्मास्युटिकल्स की बनाई गई दवा का भी ड्रग टेस्ट फ़ेल हुआ। इंटास फ़ार्मा ने 20 करोड़ के इलेक्टोरल बॉन्ड ख़रीदे और सारा चंदा BJP को दिया। 5. ग्लेनमार्क फ़ार्मा कंपनी की दवाओं के 6 ड्रग टेस्ट फ़ेल हुए। ग्लेनमार्क फ़ार्मा 9.75 करोड़ रुपए के बॉन्ड ख़रीदे और सारा चंदा BJP को दिया।",
                                         "labels": [
                                             "Corruption",
                                             "Health & Pharma",
                                             "Politics"
                                         ]
                                     },
                                     {
                                         "text": "യുഎഇ അബുദാബിയിലെയും ദുബായിലെയും എല്ലാ അറബ് മന്ത്രിമാരും അറബ് ഷേക്'മാരും റമദാൻ മാസത്തിൽ ഇന്ന് അബുദാബി ഹിന്ദു ക്ഷേത്രത്തിലെത്തി പ്രസാദത്തോടെ ക്ഷേത്രത്തിൽ റമദാൻ വ്രതം പൂർത്തിയാക്കി. (ഇതൊരു വലിയ അത്ഭുതമാണ്.) ഈ വീഡിയോ കാണുക.\uD83D\uDEA9\uD83D\uDEA9\uD83D\uDEA9\n\n",
                                         "labels": [
                                             "Foreign Policy",
                                             "Politics",
                                             "Communalism"
                                         ]
                                     }
                                 ],
                                 "languages": [
                                     "English",
                                     "Hindi",
                                     "Telugu",
                                     "Malayalam"
                                 ]
                             },
                             "callback_url": "http://example.com?callback"}}
        schema_message = schemas.parse_message(schema_input)
        result = self.classycat_model.process(schema_message)

        self.assertEqual("success", result.responseMessage)
        self.assertIsNotNone(result.schema_id)

        self.assertEqual(upload_file_to_s3_mock.call_count, 2)

        all_call_args = upload_file_to_s3_mock.call_args_list
        json_schema = all_call_args[0].args[2]
        full_schema = json.loads(json_schema)
        prompt = full_schema["prompt"]

        for language in schema_message.body.parameters["languages"]:
            self.assertIn(language, prompt)

    @patch('lib.model.classycat_schema_lookup.load_file_from_s3')
    @patch('lib.model.classycat_schema_lookup.file_exists_in_s3')
    def test_schema_lookup(self, file_exists_mock, load_file_from_s3_mock):
        # should input a schema name and return a schema id
        # the read file portion from s3 should be mocked
        file_exists_mock.return_value = True
        mock_schema_id = '123456'
        mock_schema_name = "2024 Indian Election Test"
        load_file_from_s3_mock.return_value = json.dumps(
            {
                "schema_id": mock_schema_id,
                "schema_name": mock_schema_name,
                "topics": [
                    {
                        "topic": "Politics",
                        "description": "This topic includes political claims, attacks on leaders and parties, and general political commentary."
                    },
                    {
                        "topic": "Democracy & Election Integrity",
                        "description": "This topic covers the integrity of the election process, including voter fraud, election fraud, the security of voting machines, and election interference, and electoral bonds."
                    },
                    {
                        "topic": "Economy & Growth",
                        "description": "This topic covers claims around economic growth, economic policies, GDP , employment, taxation, issues among farmer and manufacturing industry, and economic inequality."
                    },
                    {
                        "topic": "Communalism",
                        "description": "This topic covers attack on religious minorities, statements on religious freedom and polarization."
                    },
                    {
                        "topic": "Education",
                        "description": "This topic covers education policy of governments, educational institutions created, and quality of education in India."
                    },
                    {
                        "topic": "Freedom of Expression",
                        "description": "This topic covers claims regarding freedom of expression and  independence of media, and attacks on press freedom and journalists."
                    },
                    {
                        "topic": "Foreign Policy",
                        "description": "This topic covers India's relationship with neighbours and other countries, claims on effectiveness of foreign policy, international image and diplomacy."
                    },
                    {
                        "topic": "Safety of Women",
                        "description": "This topic covers the issue of safety of women and steps taken to prevent crimes against women. "
                    },
                    {
                        "topic": "Social Issues",
                        "description": "This topic covers topics on the citizenship ammendmend act and caste politics."
                    },
                    {
                        "topic": "Health & Pharma",
                        "description": "This topic covers health policies, claims on ayurveda, maternal and infant mortality, and the pharmaceutical industry."
                    },
                    {
                        "topic": "Terrorism & National Security",
                        "description": "This topics covers claims on UAPA, National security, Pakistan, and terrorism."
                    },
                    {
                        "topic": "Corruption",
                        "description": "This topic covers claims on corruptions and scams."
                    },
                    {
                        "topic": "History",
                        "description": "This topic covers claim on history of India and mythology."
                    },
                    {
                        "topic": "Science & Technology",
                        "description": "This topic covers claims on climate change, environment and science."
                    },
                    {
                        "topic": "Banking & Finance",
                        "description": "This topic covers claims around finance and banking."
                    }
                ],
                "examples": [
                    {
                        "text": "Congress Manifesto is horrible. Never seen such a dangerous manifesto in my life. It's like vision 2047 document of PFI\n\nCheck these points of manifesto\n\n1. Will bring back triple talak (Muslim personal law)\n2. Reservation to Muslim in govt n private jobs (Implement Sachchar committee report)\n3. Support Love Jihad (right to love)\n4. Support Burqa in school (right to dress)\n5. End majoritarianism (Hinduism)\n6. Ban bulldozer action\n7. Support Gaza (Hamas)\n8. Legalise Same Sex Marriage, gender fluidity, trans movement\n9. Increase Muslim judges in judiciary\n10. Communal violence bill (will stop mob lynching)\n11. Legalise beef (right to eat everything)\n12. Separate loan intrest for Muslims\n13. Allow treason (No sedition)\n\nAll those Hindu who are thinking to vote Indi Alliance, NOTA or independent. Read this and think.\n",
                        "labels": [
                            "Politics",
                            "Communalism"
                        ]
                    },
                    {
                        "text": "RSS ने अपने नागपुर मुख्यालय से 2024 लोकसभा चुनाव में कॉंग्रेस गठबंधन को समर्थन करने की घोषणा की कमाल की बात ये है कि इतनी महत्वपूर्ण खबर किसी भी news channel, और अखबार ने नहीं छापी RSS ने माना कि आज नरेंद्र मोदी भाजपा सरकार में देश का संविधान और लोकतंत्र खतरे में है इसलिए भाजपा को 2024 में रोकना अति आवश्यक है अगर देश की जनता धर्म के नशे में डूबी रही तो आने वाली नस्लें तुम्हें कभी माफ़ नहीं करेगी देश आज संकट में है और जो व्यक्ति इस समय कॉंग्रेस का साथ नहीं देगा वो भविष्य में खुद को कभी माफ़ नहीं कर पाएगा इस खबर को शेयर करके देश के एक जिम्मेदार नागरिक होने का फर्ज पूरा कीजिए",
                        "labels": [
                            "Politics",
                            "Democracy & Election Integrity"
                        ]
                    },
                    {
                        "text": "बेहद गंभीर मामला है। खबरों के मुताबिक, दवा बनाने वाली बहुत सी कंपनियां जिनकी दवाएं टेस्ट में फेल हुईं, इन कंपनियों ने इलेक्टोरल बॉन्ड से चंदा दिया। जैसे \uD83D\uDC47 1. गुजरात की कंपनी 'टोरेंट फार्मास्यूटिकल' की बनाई 3 दवाएं ड्रग टेस्ट में फेल हुईं। इस कंपनी ने BJP को 61 करोड़ का चंदा दिया। 2. सिप्ला लिमिटेड कंपनी की बनाई दवाओं के 7 बार ड्रग टेस्ट फ़ेल हुए। इस कंपनी ने BJP को 37 करोड़ का चंदा दिया। 3. सन फ़ार्मा कंपनी की बनाई गई दवाओं के 6 बार ड्रग टेस्ट फ़ेल हुए। सन फार्मा ने BJP को 31.5 करोड़ रुपए का चंदा दिया। 4. गुजरात की कंपनी इंटास फ़ार्मास्युटिकल्स की बनाई गई दवा का भी ड्रग टेस्ट फ़ेल हुआ। इंटास फ़ार्मा ने 20 करोड़ के इलेक्टोरल बॉन्ड ख़रीदे और सारा चंदा BJP को दिया। 5. ग्लेनमार्क फ़ार्मा कंपनी की दवाओं के 6 ड्रग टेस्ट फ़ेल हुए। ग्लेनमार्क फ़ार्मा 9.75 करोड़ रुपए के बॉन्ड ख़रीदे और सारा चंदा BJP को दिया।",
                        "labels": [
                            "Corruption",
                            "Health & Pharma",
                            "Politics"
                        ]
                    },
                    {
                        "text": "യുഎഇ അബുദാബിയിലെയും ദുബായിലെയും എല്ലാ അറബ് മന്ത്രിമാരും അറബ് ഷേക്'മാരും റമദാൻ മാസത്തിൽ ഇന്ന് അബുദാബി ഹിന്ദു ക്ഷേത്രത്തിലെത്തി പ്രസാദത്തോടെ ക്ഷേത്രത്തിൽ റമദാൻ വ്രതം പൂർത്തിയാക്കി. (ഇതൊരു വലിയ അത്ഭുതമാണ്.) ഈ വീഡിയോ കാണുക.\uD83D\uDEA9\uD83D\uDEA9\uD83D\uDEA9\n\n",
                        "labels": [
                            "Foreign Policy",
                            "Politics",
                            "Communalism"
                        ]
                    }
                ],
                "languages": [
                    "English",
                    "Hindi",
                    "Telugu",
                    "Malayalam"
                ]
            }
        )

        schema_lookup_input = {
            "model_name": "classycat__Model",
            "body": {
                "callback_url": "http://example.com?callback",
                "id": 1200,
                "parameters": {
                    "event_type": "schema_lookup",
                    "schema_name": mock_schema_name
                },
            }
        }

        schema_lookup_message = schemas.parse_message(schema_lookup_input)
        result = self.classycat_model.process(schema_lookup_message)

        self.assertEqual("success", result.responseMessage)
        self.assertEqual(mock_schema_id, result.schema_id)
        self.assertEqual(file_exists_mock.call_count, 1)
        self.assertEqual(load_file_from_s3_mock.call_count, 1)

    @patch('lib.model.classycat_classify.OpenRouterClient.classify')
    @patch('lib.model.classycat_classify.load_file_from_s3')
    @patch('lib.model.classycat_classify.upload_file_to_s3')
    @patch('lib.model.classycat_classify.file_exists_in_s3')
    def test_classify_success(self, file_exists_in_s3_mock, upload_file_to_s3_mock,
                              load_file_from_s3_mock, openrouter_classify_mock):
        file_exists_in_s3_mock.return_value = True
        upload_file_to_s3_mock.return_value = None
        load_file_from_s3_mock.return_value = json.dumps(
            {
                "schema_id": "123456",
                "schema_name": "2024 Indian Election Test",
                "prompt": "fake prompt hehe",
                "topics": [
                    {
                        "topic": "Politics",
                        "description": "This topic includes political claims, attacks on leaders and parties, and general political commentary."
                    },
                    {
                        "topic": "Democracy & Election Integrity",
                        "description": "This topic covers the integrity of the election process, including voter fraud, election fraud, the security of voting machines, and election interference, and electoral bonds."
                    },
                    {
                        "topic": "Economy & Growth",
                        "description": "This topic covers claims around economic growth, economic policies, GDP , employment, taxation, issues among farmer and manufacturing industry, and economic inequality."
                    },
                    {
                        "topic": "Communalism",
                        "description": "This topic covers attack on religious minorities, statements on religious freedom and polarization."
                    },
                    {
                        "topic": "Education",
                        "description": "This topic covers education policy of governments, educational institutions created, and quality of education in India."
                    },
                    {
                        "topic": "Freedom of Expression",
                        "description": "This topic covers claims regarding freedom of expression and  independence of media, and attacks on press freedom and journalists."
                    },
                    {
                        "topic": "Foreign Policy",
                        "description": "This topic covers India's relationship with neighbours and other countries, claims on effectiveness of foreign policy, international image and diplomacy."
                    },
                    {
                        "topic": "Safety of Women",
                        "description": "This topic covers the issue of safety of women and steps taken to prevent crimes against women. "
                    },
                    {
                        "topic": "Social Issues",
                        "description": "This topic covers topics on the citizenship ammendmend act and caste politics."
                    },
                    {
                        "topic": "Health & Pharma",
                        "description": "This topic covers health policies, claims on ayurveda, maternal and infant mortality, and the pharmaceutical industry."
                    },
                    {
                        "topic": "Terrorism & National Security",
                        "description": "This topics covers claims on UAPA, National security, Pakistan, and terrorism."
                    },
                    {
                        "topic": "Corruption",
                        "description": "This topic covers claims on corruptions and scams."
                    },
                    {
                        "topic": "History",
                        "description": "This topic covers claim on history of India and mythology."
                    },
                    {
                        "topic": "Science & Technology",
                        "description": "This topic covers claims on climate change, environment and science."
                    },
                    {
                        "topic": "Banking & Finance",
                        "description": "This topic covers claims around finance and banking."
                    }
                ],
                "examples": [
                    {
                        "text": "Congress Manifesto is horrible. Never seen such a dangerous manifesto in my life. It's like vision 2047 document of PFI\n\nCheck these points of manifesto\n\n1. Will bring back triple talak (Muslim personal law)\n2. Reservation to Muslim in govt n private jobs (Implement Sachchar committee report)\n3. Support Love Jihad (right to love)\n4. Support Burqa in school (right to dress)\n5. End majoritarianism (Hinduism)\n6. Ban bulldozer action\n7. Support Gaza (Hamas)\n8. Legalise Same Sex Marriage, gender fluidity, trans movement\n9. Increase Muslim judges in judiciary\n10. Communal violence bill (will stop mob lynching)\n11. Legalise beef (right to eat everything)\n12. Separate loan intrest for Muslims\n13. Allow treason (No sedition)\n\nAll those Hindu who are thinking to vote Indi Alliance, NOTA or independent. Read this and think.\n",
                        "labels": [
                            "Politics",
                            "Communalism"
                        ]
                    },
                    {
                        "text": "RSS ने अपने नागपुर मुख्यालय से 2024 लोकसभा चुनाव में कॉंग्रेस गठबंधन को समर्थन करने की घोषणा की कमाल की बात ये है कि इतनी महत्वपूर्ण खबर किसी भी news channel, और अखबार ने नहीं छापी RSS ने माना कि आज नरेंद्र मोदी भाजपा सरकार में देश का संविधान और लोकतंत्र खतरे में है इसलिए भाजपा को 2024 में रोकना अति आवश्यक है अगर देश की जनता धर्म के नशे में डूबी रही तो आने वाली नस्लें तुम्हें कभी माफ़ नहीं करेगी देश आज संकट में है और जो व्यक्ति इस समय कॉंग्रेस का साथ नहीं देगा वो भविष्य में खुद को कभी माफ़ नहीं कर पाएगा इस खबर को शेयर करके देश के एक जिम्मेदार नागरिक होने का फर्ज पूरा कीजिए",
                        "labels": [
                            "Politics",
                            "Democracy & Election Integrity"
                        ]
                    },
                    {
                        "text": "बेहद गंभीर मामला है। खबरों के मुताबिक, दवा बनाने वाली बहुत सी कंपनियां जिनकी दवाएं टेस्ट में फेल हुईं, इन कंपनियों ने इलेक्टोरल बॉन्ड से चंदा दिया। जैसे \uD83D\uDC47 1. गुजरात की कंपनी 'टोरेंट फार्मास्यूटिकल' की बनाई 3 दवाएं ड्रग टेस्ट में फेल हुईं। इस कंपनी ने BJP को 61 करोड़ का चंदा दिया। 2. सिप्ला लिमिटेड कंपनी की बनाई दवाओं के 7 बार ड्रग टेस्ट फ़ेल हुए। इस कंपनी ने BJP को 37 करोड़ का चंदा दिया। 3. सन फ़ार्मा कंपनी की बनाई गई दवाओं के 6 बार ड्रग टेस्ट फ़ेल हुए। सन फार्मा ने BJP को 31.5 करोड़ रुपए का चंदा दिया। 4. गुजरात की कंपनी इंटास फ़ार्मास्युटिकल्स की बनाई गई दवा का भी ड्रग टेस्ट फ़ेल हुआ। इंटास फ़ार्मा ने 20 करोड़ के इलेक्टोरल बॉन्ड ख़रीदे और सारा चंदा BJP को दिया। 5. ग्लेनमार्क फ़ार्मा कंपनी की दवाओं के 6 ड्रग टेस्ट फ़ेल हुए। ग्लेनमार्क फ़ार्मा 9.75 करोड़ रुपए के बॉन्ड ख़रीदे और सारा चंदा BJP को दिया।",
                        "labels": [
                            "Corruption",
                            "Health & Pharma",
                            "Politics"
                        ]
                    },
                    {
                        "text": "യുഎഇ അബുദാബിയിലെയും ദുബായിലെയും എല്ലാ അറബ് മന്ത്രിമാരും അറബ് ഷേക്'മാരും റമദാൻ മാസത്തിൽ ഇന്ന് അബുദാബി ഹിന്ദു ക്ഷേത്രത്തിലെത്തി പ്രസാദത്തോടെ ക്ഷേത്രത്തിൽ റമദാൻ വ്രതം പൂർത്തിയാക്കി. (ഇതൊരു വലിയ അത്ഭുതമാണ്.) ഈ വീഡിയോ കാണുക.\uD83D\uDEA9\uD83D\uDEA9\uD83D\uDEA9\n\n",
                        "labels": [
                            "Foreign Policy",
                            "Politics",
                            "Communalism"
                        ]
                    }
                ],
                "languages": [
                    "English",
                    "Hindi",
                    "Telugu",
                    "Malayalam"
                ]
            }
        )
        openrouter_classify_mock.return_value = "<OUTPUT>\n<CATEGORIES_0>Politics;Communalism</CATEGORIES_0>\n</OUTPUT>"
        classify_input = {
            "model_name": "classycat__Model",
            "body": {
                "id": 1200,
                "parameters": {
                    "event_type": "classify",
                    "schema_id": "4a026b82-4a16-440d-aed7-bec07af12205",
                    "items": [
                        {
                            "id": "11",
                            "text": "modi and bjp want to rule india by dividing people against each other"
                        }
                    ]
                },
                "callback_url": "http://example.com?callback"
            }
        }
        classify_message = schemas.parse_message(classify_input)
        result = self.classycat_model.process(classify_message)

        # example response for this input:
        # {"body": {"id": 1200, "content_hash": null, "callback_url": "http://example.com?callback", "url": null, "text": null, "raw": {}, "parameters": {"event_type": "classify", "schema_id": "4a026b82-4a16-440d-aed7-bec07af12205", "items": [{"id": "11", "text": "modi and bjp want to rule india by dividing people against each other"}]}, "result": {"responseMessage": "success", "classification_results": [{"id": "11", "text": "modi and bjp want to rule india by dividing people against each other", "labels": ["Politics", "Communalism"]}]}}, "model_name": "classycat.Model", "retry_count": 0}

        self.assertEqual(result.responseMessage, "success")
        self.assertEqual(len(result.classification_results), 1)
        self.assertEqual(result.classification_results[0]['id'], classify_input["body"]["parameters"]["items"][0]["id"])
        self.assertEqual(result.classification_results[0]['text'],
                         classify_input["body"]["parameters"]["items"][0]["text"])
        self.assertIn("Politics", result.classification_results[0]['labels'])
        self.assertIn("Communalism", result.classification_results[0]['labels'])
        self.assertEqual(len(result.classification_results[0]['labels']), 2)
        self.assertEqual(upload_file_to_s3_mock.call_count, 1)

    @patch('lib.model.classycat_classify.OpenRouterClient.classify')
    @patch('lib.model.classycat_classify.load_file_from_s3')
    @patch('lib.model.classycat_classify.upload_file_to_s3')
    @patch('lib.model.classycat_classify.file_exists_in_s3')
    def test_classify_fail_wrong_response_format(self, file_exists_in_s3_mock, upload_file_to_s3_mock,
                                                 load_file_from_s3_mock, openrouter_classify_mock):
        file_exists_in_s3_mock.return_value = True
        upload_file_to_s3_mock.return_value = None
        load_file_from_s3_mock.return_value = json.dumps(
            {
                "schema_id": "123456",
                "schema_name": "2024 Indian Election Test",
                "prompt": "fake prompt hehe",
                "topics": [
                    {
                        "topic": "Politics",
                        "description": "This topic includes political claims, attacks on leaders and parties, and general political commentary."
                    },
                    {
                        "topic": "Democracy & Election Integrity",
                        "description": "This topic covers the integrity of the election process, including voter fraud, election fraud, the security of voting machines, and election interference, and electoral bonds."
                    },
                    {
                        "topic": "Economy & Growth",
                        "description": "This topic covers claims around economic growth, economic policies, GDP , employment, taxation, issues among farmer and manufacturing industry, and economic inequality."
                    },
                    {
                        "topic": "Communalism",
                        "description": "This topic covers attack on religious minorities, statements on religious freedom and polarization."
                    },
                    {
                        "topic": "Education",
                        "description": "This topic covers education policy of governments, educational institutions created, and quality of education in India."
                    },
                    {
                        "topic": "Freedom of Expression",
                        "description": "This topic covers claims regarding freedom of expression and  independence of media, and attacks on press freedom and journalists."
                    },
                    {
                        "topic": "Foreign Policy",
                        "description": "This topic covers India's relationship with neighbours and other countries, claims on effectiveness of foreign policy, international image and diplomacy."
                    },
                    {
                        "topic": "Safety of Women",
                        "description": "This topic covers the issue of safety of women and steps taken to prevent crimes against women. "
                    },
                    {
                        "topic": "Social Issues",
                        "description": "This topic covers topics on the citizenship ammendmend act and caste politics."
                    },
                    {
                        "topic": "Health & Pharma",
                        "description": "This topic covers health policies, claims on ayurveda, maternal and infant mortality, and the pharmaceutical industry."
                    },
                    {
                        "topic": "Terrorism & National Security",
                        "description": "This topics covers claims on UAPA, National security, Pakistan, and terrorism."
                    },
                    {
                        "topic": "Corruption",
                        "description": "This topic covers claims on corruptions and scams."
                    },
                    {
                        "topic": "History",
                        "description": "This topic covers claim on history of India and mythology."
                    },
                    {
                        "topic": "Science & Technology",
                        "description": "This topic covers claims on climate change, environment and science."
                    },
                    {
                        "topic": "Banking & Finance",
                        "description": "This topic covers claims around finance and banking."
                    }
                ],
                "examples": [
                    {
                        "text": "Congress Manifesto is horrible. Never seen such a dangerous manifesto in my life. It's like vision 2047 document of PFI\n\nCheck these points of manifesto\n\n1. Will bring back triple talak (Muslim personal law)\n2. Reservation to Muslim in govt n private jobs (Implement Sachchar committee report)\n3. Support Love Jihad (right to love)\n4. Support Burqa in school (right to dress)\n5. End majoritarianism (Hinduism)\n6. Ban bulldozer action\n7. Support Gaza (Hamas)\n8. Legalise Same Sex Marriage, gender fluidity, trans movement\n9. Increase Muslim judges in judiciary\n10. Communal violence bill (will stop mob lynching)\n11. Legalise beef (right to eat everything)\n12. Separate loan intrest for Muslims\n13. Allow treason (No sedition)\n\nAll those Hindu who are thinking to vote Indi Alliance, NOTA or independent. Read this and think.\n",
                        "labels": [
                            "Politics",
                            "Communalism"
                        ]
                    },
                    {
                        "text": "RSS ने अपने नागपुर मुख्यालय से 2024 लोकसभा चुनाव में कॉंग्रेस गठबंधन को समर्थन करने की घोषणा की कमाल की बात ये है कि इतनी महत्वपूर्ण खबर किसी भी news channel, और अखबार ने नहीं छापी RSS ने माना कि आज नरेंद्र मोदी भाजपा सरकार में देश का संविधान और लोकतंत्र खतरे में है इसलिए भाजपा को 2024 में रोकना अति आवश्यक है अगर देश की जनता धर्म के नशे में डूबी रही तो आने वाली नस्लें तुम्हें कभी माफ़ नहीं करेगी देश आज संकट में है और जो व्यक्ति इस समय कॉंग्रेस का साथ नहीं देगा वो भविष्य में खुद को कभी माफ़ नहीं कर पाएगा इस खबर को शेयर करके देश के एक जिम्मेदार नागरिक होने का फर्ज पूरा कीजिए",
                        "labels": [
                            "Politics",
                            "Democracy & Election Integrity"
                        ]
                    },
                    {
                        "text": "बेहद गंभीर मामला है। खबरों के मुताबिक, दवा बनाने वाली बहुत सी कंपनियां जिनकी दवाएं टेस्ट में फेल हुईं, इन कंपनियों ने इलेक्टोरल बॉन्ड से चंदा दिया। जैसे \uD83D\uDC47 1. गुजरात की कंपनी 'टोरेंट फार्मास्यूटिकल' की बनाई 3 दवाएं ड्रग टेस्ट में फेल हुईं। इस कंपनी ने BJP को 61 करोड़ का चंदा दिया। 2. सिप्ला लिमिटेड कंपनी की बनाई दवाओं के 7 बार ड्रग टेस्ट फ़ेल हुए। इस कंपनी ने BJP को 37 करोड़ का चंदा दिया। 3. सन फ़ार्मा कंपनी की बनाई गई दवाओं के 6 बार ड्रग टेस्ट फ़ेल हुए। सन फार्मा ने BJP को 31.5 करोड़ रुपए का चंदा दिया। 4. गुजरात की कंपनी इंटास फ़ार्मास्युटिकल्स की बनाई गई दवा का भी ड्रग टेस्ट फ़ेल हुआ। इंटास फ़ार्मा ने 20 करोड़ के इलेक्टोरल बॉन्ड ख़रीदे और सारा चंदा BJP को दिया। 5. ग्लेनमार्क फ़ार्मा कंपनी की दवाओं के 6 ड्रग टेस्ट फ़ेल हुए। ग्लेनमार्क फ़ार्मा 9.75 करोड़ रुपए के बॉन्ड ख़रीदे और सारा चंदा BJP को दिया।",
                        "labels": [
                            "Corruption",
                            "Health & Pharma",
                            "Politics"
                        ]
                    },
                    {
                        "text": "യുഎഇ അബുദാബിയിലെയും ദുബായിലെയും എല്ലാ അറബ് മന്ത്രിമാരും അറബ് ഷേക്'മാരും റമദാൻ മാസത്തിൽ ഇന്ന് അബുദാബി ഹിന്ദു ക്ഷേത്രത്തിലെത്തി പ്രസാദത്തോടെ ക്ഷേത്രത്തിൽ റമദാൻ വ്രതം പൂർത്തിയാക്കി. (ഇതൊരു വലിയ അത്ഭുതമാണ്.) ഈ വീഡിയോ കാണുക.\uD83D\uDEA9\uD83D\uDEA9\uD83D\uDEA9\n\n",
                        "labels": [
                            "Foreign Policy",
                            "Politics",
                            "Communalism"
                        ]
                    }
                ],
                "languages": [
                    "English",
                    "Hindi",
                    "Telugu",
                    "Malayalam"
                ]
            }
        )
        openrouter_classify_mock.return_value = "<OUTPUT>\n<CATEGORIES_0>Politics;Communalism</CATEGORIES_0>\n</OUT"
        classify_input = {
            "model_name": "classycat__Model",
            "body": {
                "id": 1200,
                "parameters": {
                    "event_type": "classify",
                    "schema_id": "4a026b82-4a16-440d-aed7-bec07af12205",
                    "items": [
                        {
                            "id": "11",
                            "text": "modi and bjp want to rule india by dividing people against each other"
                        }
                    ]
                },
                "callback_url": "http://example.com?callback"
            }
        }
        classify_message = schemas.parse_message(classify_input)

        with self.assertRaises(PrestoBaseException) as e:
            self.classycat_model.process(classify_message)
            self.assertIn("Error classifying items: list index out of range", e.message)
            self.assertEqual(e.error_code, 500)

    @patch('lib.model.classycat_classify.OpenRouterClient.classify')
    @patch('lib.model.classycat_classify.load_file_from_s3')
    @patch('lib.model.classycat_classify.upload_file_to_s3')
    @patch('lib.model.classycat_classify.file_exists_in_s3')
    def test_classify_fail_wrong_number_of_results(self, file_exists_in_s3_mock, upload_file_to_s3_mock,
                                                   load_file_from_s3_mock, openrouter_classify_mock):
        file_exists_in_s3_mock.return_value = True
        upload_file_to_s3_mock.return_value = None
        load_file_from_s3_mock.return_value = json.dumps(
            {
                "schema_id": "123456",
                "schema_name": "2024 Indian Election Test",
                "prompt": "fake prompt hehe",
                "topics": [
                    {
                        "topic": "Politics",
                        "description": "This topic includes political claims, attacks on leaders and parties, and general political commentary."
                    },
                    {
                        "topic": "Democracy & Election Integrity",
                        "description": "This topic covers the integrity of the election process, including voter fraud, election fraud, the security of voting machines, and election interference, and electoral bonds."
                    },
                    {
                        "topic": "Economy & Growth",
                        "description": "This topic covers claims around economic growth, economic policies, GDP , employment, taxation, issues among farmer and manufacturing industry, and economic inequality."
                    },
                    {
                        "topic": "Communalism",
                        "description": "This topic covers attack on religious minorities, statements on religious freedom and polarization."
                    },
                    {
                        "topic": "Education",
                        "description": "This topic covers education policy of governments, educational institutions created, and quality of education in India."
                    },
                    {
                        "topic": "Freedom of Expression",
                        "description": "This topic covers claims regarding freedom of expression and  independence of media, and attacks on press freedom and journalists."
                    },
                    {
                        "topic": "Foreign Policy",
                        "description": "This topic covers India's relationship with neighbours and other countries, claims on effectiveness of foreign policy, international image and diplomacy."
                    },
                    {
                        "topic": "Safety of Women",
                        "description": "This topic covers the issue of safety of women and steps taken to prevent crimes against women. "
                    },
                    {
                        "topic": "Social Issues",
                        "description": "This topic covers topics on the citizenship ammendmend act and caste politics."
                    },
                    {
                        "topic": "Health & Pharma",
                        "description": "This topic covers health policies, claims on ayurveda, maternal and infant mortality, and the pharmaceutical industry."
                    },
                    {
                        "topic": "Terrorism & National Security",
                        "description": "This topics covers claims on UAPA, National security, Pakistan, and terrorism."
                    },
                    {
                        "topic": "Corruption",
                        "description": "This topic covers claims on corruptions and scams."
                    },
                    {
                        "topic": "History",
                        "description": "This topic covers claim on history of India and mythology."
                    },
                    {
                        "topic": "Science & Technology",
                        "description": "This topic covers claims on climate change, environment and science."
                    },
                    {
                        "topic": "Banking & Finance",
                        "description": "This topic covers claims around finance and banking."
                    }
                ],
                "examples": [
                    {
                        "text": "Congress Manifesto is horrible. Never seen such a dangerous manifesto in my life. It's like vision 2047 document of PFI\n\nCheck these points of manifesto\n\n1. Will bring back triple talak (Muslim personal law)\n2. Reservation to Muslim in govt n private jobs (Implement Sachchar committee report)\n3. Support Love Jihad (right to love)\n4. Support Burqa in school (right to dress)\n5. End majoritarianism (Hinduism)\n6. Ban bulldozer action\n7. Support Gaza (Hamas)\n8. Legalise Same Sex Marriage, gender fluidity, trans movement\n9. Increase Muslim judges in judiciary\n10. Communal violence bill (will stop mob lynching)\n11. Legalise beef (right to eat everything)\n12. Separate loan intrest for Muslims\n13. Allow treason (No sedition)\n\nAll those Hindu who are thinking to vote Indi Alliance, NOTA or independent. Read this and think.\n",
                        "labels": [
                            "Politics",
                            "Communalism"
                        ]
                    },
                    {
                        "text": "RSS ने अपने नागपुर मुख्यालय से 2024 लोकसभा चुनाव में कॉंग्रेस गठबंधन को समर्थन करने की घोषणा की कमाल की बात ये है कि इतनी महत्वपूर्ण खबर किसी भी news channel, और अखबार ने नहीं छापी RSS ने माना कि आज नरेंद्र मोदी भाजपा सरकार में देश का संविधान और लोकतंत्र खतरे में है इसलिए भाजपा को 2024 में रोकना अति आवश्यक है अगर देश की जनता धर्म के नशे में डूबी रही तो आने वाली नस्लें तुम्हें कभी माफ़ नहीं करेगी देश आज संकट में है और जो व्यक्ति इस समय कॉंग्रेस का साथ नहीं देगा वो भविष्य में खुद को कभी माफ़ नहीं कर पाएगा इस खबर को शेयर करके देश के एक जिम्मेदार नागरिक होने का फर्ज पूरा कीजिए",
                        "labels": [
                            "Politics",
                            "Democracy & Election Integrity"
                        ]
                    },
                    {
                        "text": "बेहद गंभीर मामला है। खबरों के मुताबिक, दवा बनाने वाली बहुत सी कंपनियां जिनकी दवाएं टेस्ट में फेल हुईं, इन कंपनियों ने इलेक्टोरल बॉन्ड से चंदा दिया। जैसे \uD83D\uDC47 1. गुजरात की कंपनी 'टोरेंट फार्मास्यूटिकल' की बनाई 3 दवाएं ड्रग टेस्ट में फेल हुईं। इस कंपनी ने BJP को 61 करोड़ का चंदा दिया। 2. सिप्ला लिमिटेड कंपनी की बनाई दवाओं के 7 बार ड्रग टेस्ट फ़ेल हुए। इस कंपनी ने BJP को 37 करोड़ का चंदा दिया। 3. सन फ़ार्मा कंपनी की बनाई गई दवाओं के 6 बार ड्रग टेस्ट फ़ेल हुए। सन फार्मा ने BJP को 31.5 करोड़ रुपए का चंदा दिया। 4. गुजरात की कंपनी इंटास फ़ार्मास्युटिकल्स की बनाई गई दवा का भी ड्रग टेस्ट फ़ेल हुआ। इंटास फ़ार्मा ने 20 करोड़ के इलेक्टोरल बॉन्ड ख़रीदे और सारा चंदा BJP को दिया। 5. ग्लेनमार्क फ़ार्मा कंपनी की दवाओं के 6 ड्रग टेस्ट फ़ेल हुए। ग्लेनमार्क फ़ार्मा 9.75 करोड़ रुपए के बॉन्ड ख़रीदे और सारा चंदा BJP को दिया।",
                        "labels": [
                            "Corruption",
                            "Health & Pharma",
                            "Politics"
                        ]
                    },
                    {
                        "text": "യുഎഇ അബുദാബിയിലെയും ദുബായിലെയും എല്ലാ അറബ് മന്ത്രിമാരും അറബ് ഷേക്'മാരും റമദാൻ മാസത്തിൽ ഇന്ന് അബുദാബി ഹിന്ദു ക്ഷേത്രത്തിലെത്തി പ്രസാദത്തോടെ ക്ഷേത്രത്തിൽ റമദാൻ വ്രതം പൂർത്തിയാക്കി. (ഇതൊരു വലിയ അത്ഭുതമാണ്.) ഈ വീഡിയോ കാണുക.\uD83D\uDEA9\uD83D\uDEA9\uD83D\uDEA9\n\n",
                        "labels": [
                            "Foreign Policy",
                            "Politics",
                            "Communalism"
                        ]
                    }
                ],
                "languages": [
                    "English",
                    "Hindi",
                    "Telugu",
                    "Malayalam"
                ]
            }
        )
        openrouter_classify_mock.return_value = "<OUTPUT>\n<CATEGORIES_0>Politics;Communalism</CATEGORIES_0>\n<CATEGORIES_1>Politics;Communalism</CATEGORIES_1>\n</OUTPUT>"
        classify_input = {
            "model_name": "classycat__Model",
            "body": {
                "id": 1200,
                "parameters": {
                    "event_type": "classify",
                    "schema_id": "4a026b82-4a16-440d-aed7-bec07af12205",
                    "items": [
                        {
                            "id": "11",
                            "text": "modi and bjp want to rule india by dividing people against each other"
                        }
                    ]
                },
                "callback_url": "http://example.com?callback"
            }
        }
        classify_message = schemas.parse_message(classify_input)

        with self.assertRaises(PrestoBaseException) as e:
            self.classycat_model.process(classify_message)
            self.assertIn("Not all items were classified successfully: input length 1, output length 2", e.message)
            self.assertEqual(e.error_code, 502)


    @patch('lib.model.classycat_classify.OpenRouterClient.classify')
    @patch('lib.model.classycat_classify.load_file_from_s3')
    @patch('lib.model.classycat_classify.upload_file_to_s3')
    @patch('lib.model.classycat_classify.file_exists_in_s3')
    def test_classify_some_out_of_schema_labels(self, file_exists_in_s3_mock, upload_file_to_s3_mock,
                                                     load_file_from_s3_mock, openrouter_classify_mock):
        file_exists_in_s3_mock.return_value = True
        upload_file_to_s3_mock.return_value = None
        load_file_from_s3_mock.return_value = json.dumps(
            {
                "schema_id": "123456",
                "schema_name": "2024 Indian Election Test",
                "prompt": "fake prompt hehe",
                "topics": [
                    {
                        "topic": "Politics",
                        "description": "This topic includes political claims, attacks on leaders and parties, and general political commentary."
                    },
                    {
                        "topic": "Democracy & Election Integrity",
                        "description": "This topic covers the integrity of the election process, including voter fraud, election fraud, the security of voting machines, and election interference, and electoral bonds."
                    },
                    {
                        "topic": "Economy & Growth",
                        "description": "This topic covers claims around economic growth, economic policies, GDP , employment, taxation, issues among farmer and manufacturing industry, and economic inequality."
                    },
                    {
                        "topic": "Communalism",
                        "description": "This topic covers attack on religious minorities, statements on religious freedom and polarization."
                    },
                    {
                        "topic": "Education",
                        "description": "This topic covers education policy of governments, educational institutions created, and quality of education in India."
                    },
                    {
                        "topic": "Freedom of Expression",
                        "description": "This topic covers claims regarding freedom of expression and  independence of media, and attacks on press freedom and journalists."
                    },
                    {
                        "topic": "Foreign Policy",
                        "description": "This topic covers India's relationship with neighbours and other countries, claims on effectiveness of foreign policy, international image and diplomacy."
                    },
                    {
                        "topic": "Safety of Women",
                        "description": "This topic covers the issue of safety of women and steps taken to prevent crimes against women. "
                    },
                    {
                        "topic": "Social Issues",
                        "description": "This topic covers topics on the citizenship ammendmend act and caste politics."
                    },
                    {
                        "topic": "Health & Pharma",
                        "description": "This topic covers health policies, claims on ayurveda, maternal and infant mortality, and the pharmaceutical industry."
                    },
                    {
                        "topic": "Terrorism & National Security",
                        "description": "This topics covers claims on UAPA, National security, Pakistan, and terrorism."
                    },
                    {
                        "topic": "Corruption",
                        "description": "This topic covers claims on corruptions and scams."
                    },
                    {
                        "topic": "History",
                        "description": "This topic covers claim on history of India and mythology."
                    },
                    {
                        "topic": "Science & Technology",
                        "description": "This topic covers claims on climate change, environment and science."
                    },
                    {
                        "topic": "Banking & Finance",
                        "description": "This topic covers claims around finance and banking."
                    }
                ],
                "examples": [
                    {
                        "text": "Congress Manifesto is horrible. Never seen such a dangerous manifesto in my life. It's like vision 2047 document of PFI\n\nCheck these points of manifesto\n\n1. Will bring back triple talak (Muslim personal law)\n2. Reservation to Muslim in govt n private jobs (Implement Sachchar committee report)\n3. Support Love Jihad (right to love)\n4. Support Burqa in school (right to dress)\n5. End majoritarianism (Hinduism)\n6. Ban bulldozer action\n7. Support Gaza (Hamas)\n8. Legalise Same Sex Marriage, gender fluidity, trans movement\n9. Increase Muslim judges in judiciary\n10. Communal violence bill (will stop mob lynching)\n11. Legalise beef (right to eat everything)\n12. Separate loan intrest for Muslims\n13. Allow treason (No sedition)\n\nAll those Hindu who are thinking to vote Indi Alliance, NOTA or independent. Read this and think.\n",
                        "labels": [
                            "Politics",
                            "Communalism"
                        ]
                    },
                    {
                        "text": "RSS ने अपने नागपुर मुख्यालय से 2024 लोकसभा चुनाव में कॉंग्रेस गठबंधन को समर्थन करने की घोषणा की कमाल की बात ये है कि इतनी महत्वपूर्ण खबर किसी भी news channel, और अखबार ने नहीं छापी RSS ने माना कि आज नरेंद्र मोदी भाजपा सरकार में देश का संविधान और लोकतंत्र खतरे में है इसलिए भाजपा को 2024 में रोकना अति आवश्यक है अगर देश की जनता धर्म के नशे में डूबी रही तो आने वाली नस्लें तुम्हें कभी माफ़ नहीं करेगी देश आज संकट में है और जो व्यक्ति इस समय कॉंग्रेस का साथ नहीं देगा वो भविष्य में खुद को कभी माफ़ नहीं कर पाएगा इस खबर को शेयर करके देश के एक जिम्मेदार नागरिक होने का फर्ज पूरा कीजिए",
                        "labels": [
                            "Politics",
                            "Democracy & Election Integrity"
                        ]
                    },
                    {
                        "text": "बेहद गंभीर मामला है। खबरों के मुताबिक, दवा बनाने वाली बहुत सी कंपनियां जिनकी दवाएं टेस्ट में फेल हुईं, इन कंपनियों ने इलेक्टोरल बॉन्ड से चंदा दिया। जैसे \uD83D\uDC47 1. गुजरात की कंपनी 'टोरेंट फार्मास्यूटिकल' की बनाई 3 दवाएं ड्रग टेस्ट में फेल हुईं। इस कंपनी ने BJP को 61 करोड़ का चंदा दिया। 2. सिप्ला लिमिटेड कंपनी की बनाई दवाओं के 7 बार ड्रग टेस्ट फ़ेल हुए। इस कंपनी ने BJP को 37 करोड़ का चंदा दिया। 3. सन फ़ार्मा कंपनी की बनाई गई दवाओं के 6 बार ड्रग टेस्ट फ़ेल हुए। सन फार्मा ने BJP को 31.5 करोड़ रुपए का चंदा दिया। 4. गुजरात की कंपनी इंटास फ़ार्मास्युटिकल्स की बनाई गई दवा का भी ड्रग टेस्ट फ़ेल हुआ। इंटास फ़ार्मा ने 20 करोड़ के इलेक्टोरल बॉन्ड ख़रीदे और सारा चंदा BJP को दिया। 5. ग्लेनमार्क फ़ार्मा कंपनी की दवाओं के 6 ड्रग टेस्ट फ़ेल हुए। ग्लेनमार्क फ़ार्मा 9.75 करोड़ रुपए के बॉन्ड ख़रीदे और सारा चंदा BJP को दिया।",
                        "labels": [
                            "Corruption",
                            "Health & Pharma",
                            "Politics"
                        ]
                    },
                    {
                        "text": "യുഎഇ അബുദാബിയിലെയും ദുബായിലെയും എല്ലാ അറബ് മന്ത്രിമാരും അറബ് ഷേക്'മാരും റമദാൻ മാസത്തിൽ ഇന്ന് അബുദാബി ഹിന്ദു ക്ഷേത്രത്തിലെത്തി പ്രസാദത്തോടെ ക്ഷേത്രത്തിൽ റമദാൻ വ്രതം പൂർത്തിയാക്കി. (ഇതൊരു വലിയ അത്ഭുതമാണ്.) ഈ വീഡിയോ കാണുക.\uD83D\uDEA9\uD83D\uDEA9\uD83D\uDEA9\n\n",
                        "labels": [
                            "Foreign Policy",
                            "Politics",
                            "Communalism"
                        ]
                    }
                ],
                "languages": [
                    "English",
                    "Hindi",
                    "Telugu",
                    "Malayalam"
                ]
            }
        )
        openrouter_classify_mock.return_value = "<OUTPUT>\n<CATEGORIES_0>Politics;Communalism</CATEGORIES_0>\n<CATEGORIES_1>Politico;Communism</CATEGORIES_1>\n<CATEGORIES_2>Politics;Communism</CATEGORIES_2>\n</OUTPUT>"
        classify_input = {
            "model_name": "classycat__Model",
            "body": {
                "id": 1200,
                "parameters": {
                    "event_type": "classify",
                    "schema_id": "4a026b82-4a16-440d-aed7-bec07af12205",
                    "items": [
                        {
                            "id": "11",
                            "text": "modi and bjp want to rule india by dividing people against each other"
                        },
                        {
                            "id": "12",
                            "text": "modi and bjp are amazing politicians"
                        },
                        {
                            "id": "13",
                            "text": "modi is an amazing politician"
                        }
                    ]
                },
                "callback_url": "http://example.com?callback"
            }
        }
        classify_message = schemas.parse_message(classify_input)
        result = self.classycat_model.process(classify_message)

        self.assertEqual("success", result.responseMessage)
        self.assertEqual(3, len(result.classification_results))
        self.assertListEqual(["Politics", "Communalism"], result.classification_results[0]['labels'])
        self.assertListEqual([], result.classification_results[1]['labels'])
        self.assertListEqual(["Politics"], result.classification_results[2]['labels'])

    @patch('lib.model.classycat_classify.OpenRouterClient.classify')
    @patch('lib.model.classycat_classify.load_file_from_s3')
    @patch('lib.model.classycat_classify.upload_file_to_s3')
    @patch('lib.model.classycat_classify.file_exists_in_s3')
    def test_classify_all_out_of_schema_labels(self, file_exists_in_s3_mock, upload_file_to_s3_mock,
                                                    load_file_from_s3_mock, openrouter_classify_mock):
        file_exists_in_s3_mock.return_value = True
        upload_file_to_s3_mock.return_value = None
        load_file_from_s3_mock.return_value = json.dumps(
            {
                "schema_id": "123456",
                "schema_name": "2024 Indian Election Test",
                "prompt": "fake prompt hehe",
                "topics": [
                    {
                        "topic": "Politics",
                        "description": "This topic includes political claims, attacks on leaders and parties, and general political commentary."
                    },
                    {
                        "topic": "Democracy & Election Integrity",
                        "description": "This topic covers the integrity of the election process, including voter fraud, election fraud, the security of voting machines, and election interference, and electoral bonds."
                    },
                    {
                        "topic": "Economy & Growth",
                        "description": "This topic covers claims around economic growth, economic policies, GDP , employment, taxation, issues among farmer and manufacturing industry, and economic inequality."
                    },
                    {
                        "topic": "Communalism",
                        "description": "This topic covers attack on religious minorities, statements on religious freedom and polarization."
                    },
                    {
                        "topic": "Education",
                        "description": "This topic covers education policy of governments, educational institutions created, and quality of education in India."
                    },
                    {
                        "topic": "Freedom of Expression",
                        "description": "This topic covers claims regarding freedom of expression and  independence of media, and attacks on press freedom and journalists."
                    },
                    {
                        "topic": "Foreign Policy",
                        "description": "This topic covers India's relationship with neighbours and other countries, claims on effectiveness of foreign policy, international image and diplomacy."
                    },
                    {
                        "topic": "Safety of Women",
                        "description": "This topic covers the issue of safety of women and steps taken to prevent crimes against women. "
                    },
                    {
                        "topic": "Social Issues",
                        "description": "This topic covers topics on the citizenship ammendmend act and caste politics."
                    },
                    {
                        "topic": "Health & Pharma",
                        "description": "This topic covers health policies, claims on ayurveda, maternal and infant mortality, and the pharmaceutical industry."
                    },
                    {
                        "topic": "Terrorism & National Security",
                        "description": "This topics covers claims on UAPA, National security, Pakistan, and terrorism."
                    },
                    {
                        "topic": "Corruption",
                        "description": "This topic covers claims on corruptions and scams."
                    },
                    {
                        "topic": "History",
                        "description": "This topic covers claim on history of India and mythology."
                    },
                    {
                        "topic": "Science & Technology",
                        "description": "This topic covers claims on climate change, environment and science."
                    },
                    {
                        "topic": "Banking & Finance",
                        "description": "This topic covers claims around finance and banking."
                    }
                ],
                "examples": [
                    {
                        "text": "Congress Manifesto is horrible. Never seen such a dangerous manifesto in my life. It's like vision 2047 document of PFI\n\nCheck these points of manifesto\n\n1. Will bring back triple talak (Muslim personal law)\n2. Reservation to Muslim in govt n private jobs (Implement Sachchar committee report)\n3. Support Love Jihad (right to love)\n4. Support Burqa in school (right to dress)\n5. End majoritarianism (Hinduism)\n6. Ban bulldozer action\n7. Support Gaza (Hamas)\n8. Legalise Same Sex Marriage, gender fluidity, trans movement\n9. Increase Muslim judges in judiciary\n10. Communal violence bill (will stop mob lynching)\n11. Legalise beef (right to eat everything)\n12. Separate loan intrest for Muslims\n13. Allow treason (No sedition)\n\nAll those Hindu who are thinking to vote Indi Alliance, NOTA or independent. Read this and think.\n",
                        "labels": [
                            "Politics",
                            "Communalism"
                        ]
                    },
                    {
                        "text": "RSS ने अपने नागपुर मुख्यालय से 2024 लोकसभा चुनाव में कॉंग्रेस गठबंधन को समर्थन करने की घोषणा की कमाल की बात ये है कि इतनी महत्वपूर्ण खबर किसी भी news channel, और अखबार ने नहीं छापी RSS ने माना कि आज नरेंद्र मोदी भाजपा सरकार में देश का संविधान और लोकतंत्र खतरे में है इसलिए भाजपा को 2024 में रोकना अति आवश्यक है अगर देश की जनता धर्म के नशे में डूबी रही तो आने वाली नस्लें तुम्हें कभी माफ़ नहीं करेगी देश आज संकट में है और जो व्यक्ति इस समय कॉंग्रेस का साथ नहीं देगा वो भविष्य में खुद को कभी माफ़ नहीं कर पाएगा इस खबर को शेयर करके देश के एक जिम्मेदार नागरिक होने का फर्ज पूरा कीजिए",
                        "labels": [
                            "Politics",
                            "Democracy & Election Integrity"
                        ]
                    },
                    {
                        "text": "बेहद गंभीर मामला है। खबरों के मुताबिक, दवा बनाने वाली बहुत सी कंपनियां जिनकी दवाएं टेस्ट में फेल हुईं, इन कंपनियों ने इलेक्टोरल बॉन्ड से चंदा दिया। जैसे \uD83D\uDC47 1. गुजरात की कंपनी 'टोरेंट फार्मास्यूटिकल' की बनाई 3 दवाएं ड्रग टेस्ट में फेल हुईं। इस कंपनी ने BJP को 61 करोड़ का चंदा दिया। 2. सिप्ला लिमिटेड कंपनी की बनाई दवाओं के 7 बार ड्रग टेस्ट फ़ेल हुए। इस कंपनी ने BJP को 37 करोड़ का चंदा दिया। 3. सन फ़ार्मा कंपनी की बनाई गई दवाओं के 6 बार ड्रग टेस्ट फ़ेल हुए। सन फार्मा ने BJP को 31.5 करोड़ रुपए का चंदा दिया। 4. गुजरात की कंपनी इंटास फ़ार्मास्युटिकल्स की बनाई गई दवा का भी ड्रग टेस्ट फ़ेल हुआ। इंटास फ़ार्मा ने 20 करोड़ के इलेक्टोरल बॉन्ड ख़रीदे और सारा चंदा BJP को दिया। 5. ग्लेनमार्क फ़ार्मा कंपनी की दवाओं के 6 ड्रग टेस्ट फ़ेल हुए। ग्लेनमार्क फ़ार्मा 9.75 करोड़ रुपए के बॉन्ड ख़रीदे और सारा चंदा BJP को दिया।",
                        "labels": [
                            "Corruption",
                            "Health & Pharma",
                            "Politics"
                        ]
                    },
                    {
                        "text": "യുഎഇ അബുദാബിയിലെയും ദുബായിലെയും എല്ലാ അറബ് മന്ത്രിമാരും അറബ് ഷേക്'മാരും റമദാൻ മാസത്തിൽ ഇന്ന് അബുദാബി ഹിന്ദു ക്ഷേത്രത്തിലെത്തി പ്രസാദത്തോടെ ക്ഷേത്രത്തിൽ റമദാൻ വ്രതം പൂർത്തിയാക്കി. (ഇതൊരു വലിയ അത്ഭുതമാണ്.) ഈ വീഡിയോ കാണുക.\uD83D\uDEA9\uD83D\uDEA9\uD83D\uDEA9\n\n",
                        "labels": [
                            "Foreign Policy",
                            "Politics",
                            "Communalism"
                        ]
                    }
                ],
                "languages": [
                    "English",
                    "Hindi",
                    "Telugu",
                    "Malayalam"
                ]
            }
        )
        openrouter_classify_mock.return_value = "<OUTPUT>\n<CATEGORIES_0>Politico;Communism</CATEGORIES_0>\n<CATEGORIES_1>Politico;Communism</CATEGORIES_1>\n</OUTPUT>"
        classify_input = {
            "model_name": "classycat__Model",
            "body": {
                "id": 1200,
                "parameters": {
                    "event_type": "classify",
                    "schema_id": "4a026b82-4a16-440d-aed7-bec07af12205",
                    "items": [
                        {
                            "id": "11",
                            "text": "modi and bjp want to rule india by dividing people against each other"
                        },
                        {
                            "id": "12",
                            "text": "modi and bjp are amazing politicians"
                        }
                    ]
                },
                "callback_url": "http://example.com?callback"
            }
        }
        classify_message = schemas.parse_message(classify_input)
        result = self.classycat_model.process(classify_message)

        self.assertEqual("success", result.responseMessage)
        self.assertEqual(2, len(result.classification_results))
        self.assertListEqual([], result.classification_results[0]['labels'])
        self.assertListEqual([], result.classification_results[1]['labels'])

if __name__ == '__main__':
    unittest.main()
