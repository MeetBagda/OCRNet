from mmocr.apis import TextDetInferencer, TextRecInferencer

# 1️⃣ Text Detection using DBNet
det_inferencer = TextDetInferencer(
    model='../venv310/lib/python3.10/site-packages/mmocr/.mim/configs/textdet/dbnet/dbnet_resnet18_fpnc_1200e_icdar2015.py'
)

det_result = det_inferencer('../test.jpg', return_vis=True)
print("Detection Result:")
for box in det_result['predictions']:
    print(box)

# 2️⃣ Text Recognition using CRNN
rec_inferencer = TextRecInferencer(
    model='crnn/crnn_academic.py'
)

rec_result = rec_inferencer('test.jpg', return_vis=True)
print("\nRecognition Result:")
for text in rec_result['predictions']:
    print(text)
