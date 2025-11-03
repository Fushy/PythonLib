import random

from PIL import Image
from colorama import Fore, Back, Style, init
import os

#     """¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĮįİıĴĵĶķĸĹĺĻļĽľŁłŃńŅņŇňŊŋŌōŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžƒƠơƯưȘșȚțˆˇˋ˘˙˚˛˜˝̣̀́̃̉ͺ΄΅Ά·ΈΉΊΌΎΏΐΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΪΫάέήίΰαβγδεζηθικλμνξοπρςστυφχψωϊϋόύώЁЂЃЄЅІЇЈЉЊЋЌЎЏАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяёђѓєѕіїјљњћќўџҐґҒғҖҗҘҙҚқҜҝҠҡҢңҪҫҮүҰұҲҳҶҷҸҹҺһӘәӢӣӨөӮӯԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՒՓՔՕՖ՚՛՜՝՞աբգդեզէըթժիլխծկհձղճմյնշոչպջռսվտրցւփքօֆև։֊ְֱֲֳִֵֶַָֹֺֻּֽ־ֿ׀ׁׂ׃אבגדהוזחטיךכלםמןנסעףפץצקרשתװױײ׳״،؛؟ءآأؤإئابةتثجحخدذرزسشصضطظعغـفقكلمنهوىيًٌٍَُِّْ٠١٢٣٤٥٦٧٨٩٪ٹپچڈڑژکگںھہےกขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลฦวศษสหฬอฮฯะัาำิีึืฺุู฿เแโใไๅๆ็่้๊๋์ํ๎๏๐๑๒๓๔๕๖๗๘๙๚๛ກຂຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫອຮຯະັາຳິີຶືຸູົຼຽເແໂໃໄໆ່້໊໋໌ໍ໐໑໒໓໔໕໖໗໘໙ໜໝაბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰჱჲჳჴჵჶḂḃḊḋḞḟṀṁṖṗṠṡṪṫẀẁẂẃẄẅẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ​‌‍‎‏–—―‗‘’‚“”„†‡•…‰‹›‾⁄ⁿ₤₧₪₫€₭₯№™Ω∂∆∏∑∙√∞∩∫≈≠≡≤≥⌐⌠⌡─│┌┐└┘├┤┬┴┼═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬▀▄█▌▐░▒▓■◊ﬁﬂﹱﹷﹹﹻﹽﹿﺀﺁﺂﺃﺄﺅﺈﺊﺋﺍﺎﺏﺑﺓﺕﺗﺙﺛﺝﺟﺡﺣﺥﺧﺩﺫﺭﺯﺱﺳﺵﺷﺹﺻﺽﺿﻁﻅﻇﻉﻊﻋﻌﻍﻎﻏﻐﻑﻓﻕﻗﻙﻛﻝﻟﻡﻣﻥﻧﻩﻫﻬﻭﻯﻰﻱﻲﻳﻵﻶﻷﻸﻹﻺﻻﻼ"""
ASCII_CHARS = ""
ASCII_CHARS += "█"
# ASCII_CHARS += "░"
# ASCII_CHARS += "0"
# ASCII_CHARS += "1"
# ASCII_CHARS += "0123456789"
# ASCII_CHARS = "@%#*+=-:."
# ASCII_CHARS += "AZERTYUIOPQSDFGHJKLMWXCVBN"
# ASCII_CHARS += "azertyuiopqsdfghjklmwxcvbn"
# ASCII_CHARS = list(ASCII_CHARS)
ASCII_CHARS = "".join(random.sample(ASCII_CHARS, len(ASCII_CHARS)))[0]
print(ASCII_CHARS)
init()

def rgb_to_ansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def image_to_ascii(image_path, size=None, color=False):
    try:
        # Ensure path is absolute or correctly resolved
        image_path = os.path.abspath(image_path)

        # Open image safely
        with Image.open(image_path) as img:
            if size:
                width, height = size
            else:
                width, height = img.size
            width, height = map(int, (width, height))

            aspect_ratio = height / width
            new_height = int(aspect_ratio * width * 0.55)
            img = img.resize((width, new_height))

            if color:
                img = img.convert("RGB")
            else:
                img = img.convert("L")

            pixels = list(img.getdata())
            output = ""

            for i in range(len(pixels)):
                if i % img.width == 0 and i != 0:
                    output += "\n"

                if color:
                    r, g, b = pixels[i]
                    gray = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
                    char = ASCII_CHARS[gray * len(ASCII_CHARS) // 256]
                    output += f"{rgb_to_ansi(r, g, b)}{char}{Style.RESET_ALL}"
                else:
                    gray = pixels[i]
                    char = ASCII_CHARS[gray * len(ASCII_CHARS) // 256]
                    output += char

            print(output)

    except Exception as e:
        print(f"Error: {e}")

def image_to_ascii_tft(path, tft_set, champion):
    # ratio = 256 / 151
    ratio = 256 / 120
    n = 147
    image_to_ascii(fr"{path}\tft{tft_set}_{champion.lower()}.png", color=True, size=(n * ratio, n))

if __name__ == '__main__':
    image_to_ascii_tft("image/tft/15", 15, "braum")
