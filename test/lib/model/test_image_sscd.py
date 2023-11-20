import io
import logging
import unittest
from unittest.mock import patch, Mock
from urllib.error import URLError
from typing import Dict

from lib.model.image_sscd import Model
from lib import schemas
import numpy as np

result_should_be = [-0.07144027203321457, 0.0528595857322216, -0.11396506428718567, 0.0005233244737610221,
                        -0.04154925048351288, -0.028515873476862907, -0.058826882392168045, 0.011261329986155033,
                        0.07468974590301514, 0.04327654838562012, 0.004409992601722479, 0.022582897916436195,
                        -0.06967438012361526, 0.06872913241386414, 0.0067594232968986034, -0.0035584503784775734,
                        -0.05984392389655113, 0.06857076287269592, -0.08085829019546509, -0.07211419194936752,
                        0.037366725504398346, -0.024030650034546852, 0.10351148992776871, -0.06264083832502365,
                        0.040350571274757385, 0.006679327692836523, -0.009951995685696602, 0.0161967221647501,
                        -0.008031048811972141, 0.009600456804037094, -0.024177879095077515, -0.0065284613519907,
                        0.009804324246942997, -0.02729668840765953, 0.0068421075120568275, 0.07183070480823517,
                        0.03873312473297119, -0.011135808192193508, 0.024297993630170822, 0.08706283569335938,
                        -0.011404428631067276, -0.022803163155913353, 0.014162120409309864, -0.043364185839891434,
                        -0.01327490247786045, -0.010093556717038155, -0.01574164815247059, -0.006964595057070255,
                        -0.0013869364047423005, -0.07584678381681442, 0.05398833006620407, -0.05736219510436058,
                        0.04589315876364708, -0.021578991785645485, 0.019843051210045815, -0.0006519201560877264,
                        -0.03096906468272209, 0.04863806068897247, 0.008100304752588272, 0.008826173841953278,
                        0.07164538651704788, -0.07601186633110046, -0.05091376230120659, -0.028265533968806267,
                        0.0003991558332927525, 0.042388275265693665, 0.05119031295180321, -0.01984211802482605,
                        0.029248200356960297, 0.033196162432432175, -0.030597658827900887, -0.03332706168293953,
                        0.08688798546791077, -0.030620956793427467, -0.005795127712190151, 0.026939084753394127,
                        0.04161391407251358, 0.02266402170062065, -0.04052147641777992, 0.012570186518132687,
                        0.0005767169059254229, 0.07786484807729721, 0.0015619974583387375, 0.013637062162160873,
                        0.05117057263851166, -0.02597726508975029, -0.033111896365880966, 0.0701746866106987,
                        -0.015584368258714676, 0.02364824339747429, 0.0027465904131531715, -0.04525766521692276,
                        -0.03272904083132744, 0.03058704361319542, 0.048695776611566544, -0.0582093670964241,
                        -0.0644807368516922, 0.02251230739057064, -0.0020564638543874025, -0.06945344060659409,
                        -0.01608332432806492, 0.012174352072179317, -0.0475899763405323, 0.028787409886717796,
                        0.040730882436037064, 0.025461556389927864, 0.06789694726467133, 0.062188878655433655,
                        -0.08665324747562408, 0.030804479494690895, 0.0298762246966362, 0.06593651324510574,
                        0.024233700707554817, -0.005684416741132736, -0.05876791477203369, 0.014895725063979626,
                        0.012331650592386723, -0.08530636876821518, -0.021535653620958328, -0.005839891731739044,
                        0.034899476915597916, 0.03595463186502457, 0.038640473037958145, -0.08569937944412231,
                        0.01480958517640829, 0.016735870391130447, 0.025372425094246864, 0.03038204275071621,
                        0.00031823653262108564, -0.0313514769077301, -0.12057473510503769, 0.05031529441475868,
                        0.03725805878639221, 0.014069506898522377, 0.041856229305267334, 0.007315563969314098,
                        0.038740646094083786, -0.0074793435633182526, -0.020819932222366333, 0.02455977164208889,
                        -0.08965035527944565, -0.081678107380867, 0.057668622583150864, 0.05913791060447693,
                        -0.006911333184689283, -0.048169031739234924, -0.0727081224322319, -0.10594800114631653,
                        0.05663284659385681, -0.019163984805345535, -0.04517679288983345, 0.02395869605243206,
                        0.041778430342674255, -0.09522789716720581, 0.009570611640810966, 0.030647773295640945,
                        0.02276058867573738, -0.0376124233007431, -0.06889466941356659, -0.029664795845746994,
                        0.06314549595117569, 0.030073754489421844, 0.0359380878508091, -0.021464575082063675,
                        0.02590654045343399, 0.09144120663404465, -0.026760267093777657, 0.004901545587927103,
                        0.03806091472506523, -0.02291925437748432, 0.011413888074457645, -0.01821034960448742,
                        0.070054791867733, -0.01789053902029991, 0.02784998156130314, 0.038003288209438324,
                        -0.015555726364254951, -0.06261636316776276, 0.10744502395391464, 0.028204796835780144,
                        0.039750680327415466, -0.006700362078845501, 0.0014031894970685244, -0.006510741543024778,
                        0.010954192839562893, -0.0265719722956419, 0.04018286615610123, 0.03822746500372887,
                        0.06522148102521896, 0.026165448129177094, -0.010680162347853184, 0.02104169689118862,
                        0.039393555372953415, -0.054629307240247726, 0.052427515387535095, -0.05568528175354004,
                        -0.05142313614487648, 0.02597949653863907, 0.03633121773600578, -0.005130075383931398,
                        -0.019111020490527153, 0.014608109369874, 0.010372712276875973, -0.004220862407237291,
                        0.00493678729981184, 0.062161609530448914, 0.019215654581785202, -0.03241828829050064,
                        -0.03072202019393444, 0.023111265152692795, -0.007216483820229769, 0.036560285836458206,
                        0.01290745846927166, -0.07817694544792175, -0.013376968912780285, -0.05606372654438019,
                        0.051513757556676865, -0.012899071909487247, -0.06157049909234047, -0.08024762570858002,
                        0.04888973385095596, 0.01188365463167429, 0.009882175363600254, -0.019134674221277237,
                        0.024625474587082863, -0.006905965507030487, -0.030667953193187714, 0.01298027578741312,
                        0.018715037032961845, -0.026403281837701797, -0.00783504731953144, 0.004286203999072313,
                        0.0010807081125676632, -0.00660742586478591, -0.023812497034668922, 0.06302206218242645,
                        -0.057830214500427246, -0.03886802867054939, 0.024021243676543236, -0.055729299783706665,
                        -0.10672368109226227, 0.030587900429964066, 0.028457045555114746, 0.04784972965717316,
                        0.03260587900876999, 0.06271659582853317, -0.10934319347143173, 0.035900115966796875,
                        -0.04468424990773201, 0.07048524171113968, 0.05516570061445236, 0.03436368331313133,
                        0.00997652392834425, 0.08526262640953064, -0.03130404278635979, 0.005957255605608225,
                        0.06824888288974762, -0.036280177533626556, 0.06230608746409416, -0.021922865882515907,
                        -0.010930586606264114, 0.01367107778787613, -0.018288403749465942, 0.0489020049571991,
                        -0.04091630131006241, -0.030513420701026917, -0.020151210948824883, -0.023531029000878334,
                        -0.09813980013132095, -0.02391956001520157, -0.007604392245411873, 0.04859378933906555,
                        -0.00860443152487278, -0.05193145573139191, 0.015980644151568413, -0.0075520663522183895,
                        -0.008378726430237293, 9.938422590494156e-05, 0.03541550040245056, -0.04212876781821251,
                        0.058003149926662445, -0.022017791867256165, 0.052691467106342316, 0.09577743709087372,
                        0.02856585755944252, -4.2199459130642936e-05, 0.005996208172291517, -0.10965994000434875,
                        0.02336238883435726, 0.02216327004134655, 0.04850497841835022, -0.005761938635259867,
                        0.044221676886081696, -0.0089781004935503, -0.03918464109301567, 0.011156989261507988,
                        -0.030580462887883186, 0.09308770298957825, 0.025906618684530258, -0.029887555167078972,
                        0.04069322720170021, -0.016283219680190086, -0.025910494849085808, 0.0012494147522374988,
                        0.0031355945393443108, 0.015254073776304722, 0.060300517827272415, 0.0007453417056240141,
                        -0.021660279482603073, -0.06608810275793076, 0.008861289359629154, -0.00020786059030797333,
                        0.017373064532876015, -0.002692391164600849, 0.026701727882027626, 0.04024803638458252,
                        -0.016312239691615105, 0.031316451728343964, 0.008049928583204746, 0.04411536455154419,
                        0.07697759568691254, -0.043828073889017105, 0.016851941123604774, 0.06488212943077087,
                        -0.06394548714160919, -0.004850515630096197, -0.06142564117908478, -0.0007274787058122456,
                        -0.000708505162037909, -0.010618982836604118, 0.07141107320785522, -0.06414534151554108,
                        0.09092477709054947, -0.015697801485657692, -0.12162954360246658, 0.01604246161878109,
                        -0.0338786318898201, 0.043666157871484756, 0.015039476566016674, 0.04161584749817848,
                        0.024161431938409805, 0.0301087386906147, 0.003925960510969162, -0.06638433784246445,
                        -0.014072329737246037, 0.044508274644613266, 0.000865419686306268, 0.028618697077035904,
                        0.007238695397973061, -0.025417087599635124, 0.030697954818606377, -0.026795875281095505,
                        0.09330523759126663, -0.02380654215812683, 0.0354798324406147, 0.03782563656568527,
                        0.015322495251893997, 0.017190296202898026, 0.01645561493933201, 0.07070869207382202,
                        0.044643379747867584, -0.09219500422477722, -0.027271369472146034, 0.021323859691619873,
                        0.019855061545968056, -0.08344972878694534, 0.02964773029088974, 0.022371770814061165,
                        0.010329704731702805, 0.0204318817704916, 0.013014006428420544, -0.04265967756509781,
                        0.0034814556129276752, 0.005503968335688114, -0.011838463135063648, -0.09120689332485199,
                        0.00863907765597105, -0.016315268352627754, -0.053035762161016464, -0.018841488286852837,
                        0.029966143891215324, -0.007713795639574528, 0.015808969736099243, -0.0423244871199131,
                        0.006674240343272686, 0.05231969803571701, -0.02070920541882515, 0.06744643300771713,
                        0.11502596735954285, -0.03222789987921715, 0.025131283327937126, 0.12610262632369995,
                        -0.008005252107977867, 0.08683951944112778, -0.016409732401371002, -0.05496629700064659,
                        -0.018000662326812744, 0.059494391083717346, -0.033545736223459244, 0.009159487672150135,
                        -0.014886717312037945, -0.03672671318054199, -0.0382157601416111, -0.07774834334850311,
                        0.04587544873356819, 0.013530625030398369, 0.03489874303340912, -0.01647481694817543,
                        -0.018000798299908638, 0.03171844035387039, -0.040251001715660095, -0.04073946923017502,
                        0.06595395505428314, -0.03739870339632034, 0.014373987913131714, -0.035246916115283966,
                        -0.0062555354088544846, 0.03349122777581215, -0.02458479069173336, -0.01668730564415455,
                        0.11991753429174423, -0.12086635082960129, -0.005912070628255606, 0.01163905207067728,
                        0.036334726959466934, -0.010278688743710518, -0.04652582108974457, -0.0005802358500659466,
                        -0.08215046674013138, 0.07692704349756241, -0.005483880639076233, 0.019933341071009636,
                        0.0025862606707960367, 0.020065804943442345, -0.00863591581583023, 0.07357700914144516,
                        0.004476140718907118, -0.012785458005964756, -0.03159927949309349, -0.046191293746232986,
                        -0.002030089497566223, 0.03555852919816971, -0.024284178391098976, 0.04600340500473976,
                        0.03603901341557503, 0.0018025911413133144, -0.13817547261714935, 0.05801040306687355,
                        0.03214746713638306, -0.09996572881937027, -0.018432531505823135, -0.05093832314014435,
                        -0.03224610909819603, -0.01639450527727604, -0.010061380453407764, 0.055063556879758835,
                        -0.08065234124660492, -0.007862106896936893, -0.021783823147416115, -0.052751604467630386,
                        -0.0691704973578453, 0.04986613243818283, -0.015607778914272785, 0.03232172876596451,
                        0.02679631859064102, 0.0036959717981517315, -0.030126234516501427, -0.02326115220785141,
                        -0.006363472435623407, 0.015963030979037285, 0.00330563192255795, -0.024462511762976646,
                        0.01190184149891138, 0.003605007426813245, -0.050289880484342575, 0.0266175027936697,
                        0.05349498614668846, -0.008247151039540768, -0.06670569628477097, 0.06351006031036377,
                        0.08114060759544373, -0.006813893094658852, 0.024257315322756767, -0.03206257149577141,
                        0.010035752318799496, -0.06654676049947739, 0.012111213989555836, -0.056731320917606354,
                        0.024231307208538055, -0.024802042171359062, 0.02894349955022335, 0.08170276880264282,
                        0.011898127384483814, 0.006088235415518284, -0.03856944665312767, 0.09566926956176758,
                        0.005668847355991602, -0.010908310301601887, -0.044969141483306885, -0.0032908024732023478,
                        0.016451604664325714, 0.030626192688941956, 0.027100708335638046, -0.004937123507261276,
                        -0.01188697014003992, 0.0018644103547558188, 0.028558410704135895, -0.05996338650584221,
                        -0.033904775977134705, 0.00781658198684454, 0.005846137646585703, 0.022124793380498886]

class TestModel(unittest.TestCase):

    @patch("torchvision.transforms")
    def test_compute_sscd(self, mock_pdq_hasher):
        with open("img/presto_flowchart.jpg", "rb") as file:
            image_content = file.read()
        # mock_hasher_instance = mock_pdq_hasher.return_value
        # mock_hasher_instance.fromBufferedImage.return_value.getHash.return_value.dumpBitsFlat.return_value = '1001'
        result = Model().compute_sscd(io.BytesIO(image_content))
        self.assertTrue(np.allclose(result, result_should_be))

    @patch("urllib.request.urlopen")
    def test_get_iobytes_for_image(self, mock_urlopen):
        with open("img/presto_flowchart.jpg", "rb") as file:
            image_content = file.read()
        mock_response = Mock()
        mock_response.read.return_value = image_content
        mock_urlopen.return_value = mock_response
        image = schemas.Message(body={"id": "123", "callback_url": "http://example.com?callback", "url": "http://example.com/image.jpg"}, model_name="audio__Model")
        result = Model().get_iobytes_for_image(image)
        self.assertIsInstance(result, io.BytesIO)
        self.assertEqual(result.read(), image_content)

    @patch("urllib.request.urlopen")
    def test_get_iobytes_for_image_raises_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError('test error')
        image = schemas.Message(body={"id": "123", "callback_url": "http://example.com?callback", "url": "http://example.com/image.jpg"}, model_name="audio__Model")
        with self.assertRaises(URLError):
            Model().get_iobytes_for_image(image)

    @patch.object(Model, "get_iobytes_for_image")
    @patch.object(Model, "compute_sscd")
    def test_process(self, mock_compute_pdq, mock_get_iobytes_for_image):
        mock_compute_pdq.return_value = result_should_be
        mock_get_iobytes_for_image.return_value = io.BytesIO(b"image_bytes")
        image = schemas.Message(body={"id": "123", "callback_url": "http://example.com?callback", "url": "http://example.com/image.jpg"}, model_name="audio__Model")
        result = Model().process(image)
        self.assertEqual(result, result_should_be)


if __name__ == "__main__":
    unittest.main()
