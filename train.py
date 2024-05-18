import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dropout, GlobalAveragePooling2D, Dense
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, LearningRateScheduler

# 이미지 데이터 경로
IMG_SAVE_PATH = 'image_data'

# 클래스 맵핑
CLASS_MAP = {
    "paper": 0,
    "rock": 1,
    "scissors": 2,
    "none": 3
}
NUM_CLASSES = 3

def get_model():
    base_model = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
    base_model.trainable = False  # 기본 모델 고정
    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dropout(0.5),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(NUM_CLASSES, activation='softmax')  # 출력 레이어의 뉴런 수를 클래스 수와 일치시킴
    ])
    return model


# 데이터 증강 및 분할 설정
data_gen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255,  # 여기에 정규화 추가
    rotation_range=20,  # 회전 범위 축소
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2
)

train_data_gen = data_gen.flow_from_directory(
    IMG_SAVE_PATH,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',  # 클래스 모드를 categorical로 설정
    subset='training'
)

val_data_gen = data_gen.flow_from_directory(
    IMG_SAVE_PATH,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',  # 클래스 모드를 categorical로 설정
    subset='validation'
)

# 모델 정의 및 컴파일
model = get_model()
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
              loss='categorical_crossentropy',  # categorical_crossentropy 손실 함수 사용
              metrics=['accuracy'])


# 콜백 정의
def lr_schedule(epoch):
    return 0.001 if epoch < 10 else 0.0005 if epoch < 20 else 0.0001

lr_scheduler = LearningRateScheduler(lr_schedule)
early_stopper = EarlyStopping(monitor='val_loss', patience=10)
# 모델 체크포인트
model_checkpoint = ModelCheckpoint('best_model.keras', save_best_only=True)  # save_format 인자 제거

# 모델 훈련
model.fit(
    train_data_gen,
    epochs=30,
    validation_data=val_data_gen,
    callbacks=[early_stopper, model_checkpoint, lr_scheduler]
)

# 모델 저장 (SavedModel 형식으로 저장)
model.save("rock-paper-scissors-model.keras")
