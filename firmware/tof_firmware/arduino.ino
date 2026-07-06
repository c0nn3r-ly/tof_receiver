#include <Wire.h>
#include <VL53L0X.h>

VL53L0X sensor;

// 每个通道传感器是否初始化成功（持久记录）
bool initOk[4] = {false, false, false, false};

// 切换 TCA9548A 通道
void selectI2CChannel(uint8_t channel) {
  if (channel > 7) return;
  Wire.beginTransmission(0x70);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200); // 串口初始化
  Wire.begin(21, 22);   // I2C 初始化 (21=SDA, 22=SCL)

  // 初始化 4 个通道上的传感器
  for (uint8_t i = 0; i < 4; i++) {
    selectI2CChannel(i);
    sensor.setTimeout(500);
    if (sensor.init()) {
      sensor.startContinuous();
      initOk[i] = true;
    }
    else
    {
      initOk[i] = false;
    }
  }
}

void loop() {
  int16_t distances[4];
  bool health[4];

  // 循环读取 4 路数据
  for (uint8_t i = 0; i < 4; i++) {
    selectI2CChannel(i);
    distances[i] = sensor.readRangeContinuousMillimeters();
    // 健康 = 初始化成功 且 未发生超时 且 读数合法
    // readRangeContinuousMillimeters() 超时会返回 65535
    // 这里 如果某一个值卡住了 readRangeCon什么玩意的 会 timeout 500ms 然后 in case 把传感器的频率压到 0.5Hz 
    // 可以考虑要不要改 理论上 100ms 就够了，这玩意通信不能这么慢吧 @HUINAN0213
    health[i] = initOk[i] && !sensor.timeoutOccurred() && distances[i] > 0 && distances[i] < 8000;
  }

  // ── 通过物理串口发送文本 ──
  // 格式：d0,d1,d2,d3,h0,h1,h2,h3  （前 4 个距离 mm，后 4 个健康 0/1）
  Serial.print(distances[0]); Serial.print(",");
  Serial.print(distances[1]); Serial.print(",");
  Serial.print(distances[2]); Serial.print(",");
  Serial.print(distances[3]);
  Serial.print(",");
  Serial.print(health[0] ? 1 : 0);
  Serial.print(",");
  Serial.print(health[1] ? 1 : 0);
  Serial.print(",");
  Serial.print(health[2] ? 1 : 0);
  Serial.print(",");
  Serial.println(health[3] ? 1 : 0); // 以换行符结尾

  delay(20); // 50Hz 的刷新率
}
