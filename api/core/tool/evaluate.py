from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness, context_precision
import os


def test():
    os.environ["OPENAI_API_KEY"] = ""

    questions = ['please introduce iphone 7']

    # context = [
    #     'The iPhone 7 and 7 Plus were announced on September 7, 2016, which introduced larger camera sensors, IP67-certified water and dust resistance, and a quad-core A10 Fusion processor utilizing big.LITTLE technology;[38] the 3.5 mm headphone jack was removed, and was followed by the introduction of the AirPods wireless earbuds.[39] Optical image stabilization was added to the 7\'s camera. A second telephoto camera lens was added on the 7 Plus, enabling two-times optical zoom, and "Portrait" photography mode which simulates bokeh in photos.[40]Cosmetic']
    context = ['The iPhone 7 and 7 Plus were announced on September 7, 2016, which introduced larger camera sensors, IP67-certified water and dust resistance, and a quad-core A10 Fusion processor utilizing big.LITTLE technology;[38] the 3.5 mm headphone jack was removed, and was followed by the introduction of the AirPods wireless earbuds.[39] Optical image stabilization was added to the 7\'s camera. A second telephoto camera lens was added on the 7 Plus, enabling two-times optical zoom, and "Portrait" photography mode which simulates bokeh in photos.[40]', 'The iPhone 14, 14 Plus, 14 Pro, and 14 Pro Max were announced on September 7, 2022. All models introduced satellite phone emergency calling functionality. The iPhone 14 Plus introduced the large 6.7-inch screen size, first seen on the iPhone 12 Pro Max, into a lower-cost device.[54] The iPhone 14 Pro and 14 Pro Max additionally introduced a higher-resolution 48-megapixel main camera, the first increase in megapixel count since', 'the iPhone 6s; it also introduced always-on display technology to the lock screen, and an interactive status bar interface integrated in a redesigned screen cutout, entitled "Dynamic Island".[55]The iPhone 6s and 6s Plus were introduced on September 9, 2015, and included a more bend-resistant frame made of a stronger aluminum alloy, as well as a higher resolution 12 megapixel main camera capable of 4K video recording.[36] The first-generation iPhone SE was introduced on March 21, 2016, and was a low-cost device that incorporated newer hardware from the iPhone 6s, in the frame of the older iPhone 5s.[37]The iPhone 13, 13 Mini, 13 Pro, and 13 Pro Max were announced via a livestream event on September 14, 2021. All models featured larger camera sensors, larger batteries for longer battery life, and a narrower "notch" screen cutout.[52] ','The iPhone 13 Pro and 13 Pro Max additionally introduced smoother adaptive 120 Hz refresh rate "ProMotion" technology in its OLED display, and three-times optical zoom in the telephoto lens.[53] The low-cost third-generation iPhone SE was introduced on March 8, 2022, and incorporated the A15 Bionic chip from the iPhone 13, but otherwise retained similar hardware to the second-generation iPhone SE.','The iPhone 8, 8 Plus, and iPhone X were announced on September 12, 2017, in Apple\'s first event held at the Steve Jobs Theater in Apple Park. All models featured rear glass panel designs akin to the iPhone 4, wireless charging, and a hexa-core A11 Bionic chip with "Neural Engine" AI accelerator hardware. The iPhone X additionally introduced a 5.8-inch OLED "Super Retina" display with a "bezel-less" design, with a higher pixel density and contrast ratio than previous iPhones with LCD displays, and introduced a stronger frame made of stainless steel. It also introduced Face ID facial recognition authentication hardware, in a "notch" screen cutout, in place of Touch ID;[41][42] the home button was removed to make room for additional screen space, replacing it with a gesture-based navigation system.[43] At its US$999 starting price, the iPhone X was the most expensive iPhone at launch.[44]']
    contexts = [context]
    #answers = ['The iPhone 7 was released in 2016 and featured larger camera sensors, water and dust resistance, and a faster processor. It also had some notable changes, such as the removal of the 3.5 mm headphone jack and the introduction of the AirPods wireless earbuds. The camera on the iPhone 7 Plus had a second telephoto lens for optical zoom and a "Portrait" photography mode.']
    answers =['The iPhone 7 was announced on September 7, 2016. It came with larger camera sensors, water and dust resistance (IP67-certified), and a quad-core A10 Fusion processor. The 3.5 mm headphone jack was removed, and instead, Apple introduced the AirPods wireless earbuds. The iPhone 7 also added optical image stabilization to its camera. The iPhone 7 Plus, a variant of the iPhone 7, included a second telephoto camera lens that allowed for two-times optical zoom and introduced the "Portrait" photography mode, which simulated bokeh in photos.']
    # prepare your huggingface dataset in the format
    ds = Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
        }
    )

    result = evaluate(ds, [answer_relevancy, context_precision, faithfulness])
    print(result)
